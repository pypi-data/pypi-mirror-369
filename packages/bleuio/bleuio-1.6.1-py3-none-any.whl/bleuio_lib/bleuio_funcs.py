# (C) 2024 Smart Sensor Devices AB

import sys
import threading
import time
import json
import signal
import atexit
from copy import deepcopy

import serial.tools.list_ports

DONGLE_ARRAY = []

DUAL = "dual"
CENTRAL = "central"
PERIPHERAL = "peripheral"

# version: 1.6.0
# updated: 2024-11-26


class BleuIO(object):
    def __init__(self, port="auto", baud=115200, timeout=0.01, debug=False):
        """
        Initiates the dongle. If port param is left as 'auto' it will auto-detect if bleuio dongle is connected.
        :param port: str
        :param baud: int
        :param timeout: int
        :param debug: bool
        """
        self.block_time = timeout
        retry_count = 0
        self._serial = None
        self._port = None
        self.fwVersion = ""
        self.dongleTypeStd = False
        self._debug = debug
        self.__cmdDone = False
        self.__saveScanRsp = False
        self.__saveEvtRsp = False
        self.receiver_thread = None
        self._reader_alive = None
        self._evt_cb = None
        self._scan_cb = None
        self.gaproles = self.GapRoles()
        self.status = self.BLEStatus()
        self.__threadLock = threading.Lock()

        # Constants
        self.UUID = "UUID"
        self.CHAR_PROPERTY = "PROP"
        self.CHAR_PERMISSION = "PERM"
        self.CHAR_LENGTH = "LEN"
        self.CHAR_VALUE = "VALUE"
        self.CHAR_HEX_VALUE = "VALUEB"
        self.DESC_PERMISSION = "DPERM"
        self.DESC_LENGTH = "DLEN"
        self.DESC_VALUE = "DVALUE"
        self.DESC_HEX_VALUE = "DVALUEB"
        self.NAME = "DVALUE"
        self.MFSID = "MFSID"
        self.CLEAR = "CLEAR"

        if port == "auto":
            dongle_count = 1
            port_list = []
            while len(DONGLE_ARRAY) == 0 and retry_count < 10:
                all_ports = serial.tools.list_ports.comports(include_links=False)
                for d_port in all_ports:
                    if str(d_port.hwid).__contains__("VID:PID=2DCF"):
                        bleuio_dongle = (
                            str(dongle_count) + ") " + d_port.device + " " + d_port.hwid
                        )
                        if bleuio_dongle.__contains__("VID:PID=2DCF:6002"):
                            if self._debug:
                                print("Found dongle in port: " + d_port.device)
                            DONGLE_ARRAY.append(bleuio_dongle)
                            port_list.append(d_port)
                            dongle_count += 1
                        if bleuio_dongle.__contains__("VID:PID=2DCF:6001"):
                            if self._debug:
                                print("Bootloader in port: " + d_port.device)
                            time.sleep(2)
                            retry_count = 0
                    else:
                        pass
                retry_count += 1

            port_idx = 0
            dongle_count = dongle_count - 1
            if self._debug:
                print("Dongles found: " + str(dongle_count))
            while self._serial is None and dongle_count > 0:
                if self._debug:
                    print("Trying port: " + str(port_list[port_idx].device))
                try:
                    self._serial = serial.Serial(
                        port=port_list[port_idx].device, baudrate=baud, timeout=timeout
                    )
                    self._port = port_list[port_idx].device
                except (serial.SerialException, IndexError):
                    dongle_count = dongle_count - 1
                    self._serial = None
                    if dongle_count == 0:
                        print("No dongle COM port avaliable!")
                        raise
                    if self._debug:
                        print(
                            "Port: "
                            + str(port_list[port_idx].device)
                            + " unavalible... Looking for other dongle to connect to..."
                        )
                    port_idx = port_idx + 1

        else:
            if not isinstance(port, str):
                raise ValueError("Invalid port specified: {}".format(port))
            while self._serial is None:
                try:
                    self._serial = serial.Serial(
                        port=port, baudrate=baud, timeout=timeout, write_timeout=timeout
                    )
                    self._port = port
                except (ValueError, serial.SerialException) as e:
                    retry_count += 1
                    if retry_count > 3:
                        print("Error: " + str(e))
                        print("Make sure the dongle is not already in use.")
                        exit()
                    else:
                        if self._debug:
                            print(
                                "Error occurred while trying to open port. "
                                + str(e)
                                + " Retrying",
                                retry_count,
                                "/",
                                3,
                                "...",
                            )
                        time.sleep(5)

            self._serial.flushInput()
            self._serial.flushOutput()

        signal.signal(signal.SIGINT, self.__signal_handler)
        atexit.register(self.exit_handler)

        # rx task state
        self.rx_buffer = b""
        self.rx_response = []
        self.rx_scanning_results = []
        self.rx_evt_results = []

        self._start_reader()
        self._serial.write("QUIT\r".encode())
        self.send_command("stop")
        self.send_command("ATV1")
        self.send_command("ATE1")
        self.send_command("ATI")
        # end of BleuIO.__init__()

    class BLEStatus:
        def __init__(self):
            """A class used to handle BLE Statuses

            :attr isScanning: Keeps track on if dongle is currently scanning.
            :attr isConnected: Keeps track on if dongle is currently connected.
            :attr isAdvertising: Keeps track on if dongle is currently advertising.
            :attr isSPSStreamOn: Keeps track on if dongle is currently in SPS stream mode.
            :attr role: Keeps track of the dongle's current GAP Role.
            """
            self.isScanning = False
            self.isConnected = False
            self.isAdvertising = False
            self.isSPSStreamOn = False
            self.role = ""
            # self.connectedList = []
            # self.numberOfConnections = 0

    class GapRoles:
        def __init__(self):
            """A class used to handle the different GAP Roles

            :attr PERIPHERAL:
            :attr CENTRAL:
            :attr DUAL:
            """
            self.PERIPHERAL = "peripheral"
            self.CENTRAL = "central"
            self.DUAL = "dual"

    class BleuIORESP:
        def __init__(self):
            """A class used to handle the different Dongle Responses

            :attr Cmd: Contains the command data.
            :attr Ack: Contains the acknowledge data.
            :attr Rsp: Contains list of the response data.
            :attr End: Contains the end data.
            """
            self.Cmd = None
            self.Ack = None
            self.Rsp = []
            self.End = None

    class BleuIOException(Exception):
        pass

    def __signal_handler(self, signum, frame):
        if self._debug:
            print("Exit Signal Handler...")
        sys.exit(1)

    def __parseRspIntoJSON(self, inputData, careObj):
        response = deepcopy(inputData)
        newResp = []

        # Check for multilines in elements
        for lines in response:
            if b"\r" in lines or b"\n" in lines:
                if self._debug:
                    print("\r\nCR found in line!")
                for line in lines.splitlines():
                    if not line == b"":
                        newResp.append(line)
                response = newResp

        try:
            for line in response:
                if ('{"C"') in line.decode("utf-8", "ignore"):
                    careObj.Cmd = json.loads(line)
                if ('{"A"') in line.decode("utf-8", "ignore"):
                    careObj.Ack = json.loads(line)
                if ('{"R"') in line.decode("utf-8", "ignore"):
                    careObj.Rsp.append(json.loads(line))
                if ('{"E"') in line.decode("utf-8", "ignore"):
                    careObj.End = json.loads(line)
                if ('{"SE":') in line.decode("utf-8", "ignore"):
                    careObj.Ack = json.loads(line)
        except Exception as e:
            raise self.BleuIOException(
                "Exception: "
                + str(e)
                + "\r\nError line: "
                + str(line)
                + "\r\n(Response: "
                + str(response)
                + ")"
            )
        if self._debug:
            try:
                print("debug(__parseRspIntoJSON response): " + str(response))
                print("debug(__parseRspIntoJSON line): " + str(line))
            except Exception:
                pass

    def exit_handler(self):
        if self._debug:
            print("Exit Handler Cleanup...")
        if self._serial.is_open:
            try:
                self._serial.write("\x03".encode())
                self._serial.write("\x1B".encode())
                self._stop_reader()
                self._serial.close()
            except Exception:
                pass

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->reader thread
        self.receiver_thread = threading.Thread(target=self.__poll_serial, name="rx")
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        self.receiver_thread.join()

    def __poll_serial(self):
        """Polls Dongle RX Data"""
        while self._reader_alive:
            try:
                self.rx_buffer += self._serial.read(self._serial.in_waiting)
                if self.rx_buffer and self.rx_buffer[-1:] == b"\n":
                    if str.encode('"action":"scan completed"') in self.rx_buffer:
                        self.__threadLock.acquire()
                        self.status.isScanning = False
                        self.__saveScanRsp = False
                        self.__threadLock.release()
                        if not self.__cmdDone:
                            self.__threadLock.acquire()
                            self.__cmdDone = True
                            self.rx_response.append(self.rx_buffer)
                            self.__threadLock.release()

                    if str.encode('"action":"scanning"') in self.rx_buffer:
                        self.__threadLock.acquire()
                        self.status.isScanning = True
                        self.__threadLock.release()

                    if str.encode('"action":"streaming"') in self.rx_buffer:
                        self.__threadLock.acquire()
                        self.status.isSPSStreamOn = True
                        self.__threadLock.release()

                    if str.encode('"action":"not streaming"') in self.rx_buffer:
                        self.__threadLock.acquire()
                        self.status.isSPSStreamOn = False
                        self.__threadLock.release()
                        if not self.__cmdDone:
                            self.__threadLock.acquire()
                            self.__cmdDone = True
                            self.__threadLock.release()
                            decoded_SPSStream_result = self.rx_buffer.decode(
                                "utf-8", "ignore"
                            )
                            decoded_SPSStream_resultList = []
                            decoded_SPSStream_resultList = (
                                decoded_SPSStream_result.split("\r\n")
                            )
                            for line in decoded_SPSStream_resultList:
                                if line:
                                    if ('{"R"') in line:
                                        self.rx_response.append(line.encode())

                    if str.encode('"action":"advertising stopped"') in self.rx_buffer:
                        self.__threadLock.acquire()
                        self.status.isAdvertising = False
                        self.__threadLock.release()

                    if str.encode('"action":"advertising"') in self.rx_buffer:
                        self.__threadLock.acquire()
                        self.status.isAdvertising = True
                        self.__threadLock.release()

                    if str.encode('"action":"connected"') in self.rx_buffer:
                        self.__threadLock.acquire()
                        self.status.isConnected = True
                        self.__threadLock.release()  # "action":"disconnected"

                    if str.encode('"action":"disconnected"') in self.rx_buffer:
                        self.__threadLock.acquire()
                        self.status.isConnected = False
                        self.__threadLock.release()

                    if str.encode('"evt":') in self.rx_buffer and self.__saveEvtRsp:
                        if self._evt_cb != None:
                            decoded_evt_result = self.rx_buffer.decode(
                                "utf-8", "ignore"
                            )
                            decoded_evt_resultList = []
                            decoded_evt_resultList = decoded_evt_result.split("\r\n")
                            for line in decoded_evt_resultList:
                                if line:
                                    if ('"evt":') in line:
                                        self.rx_evt_results.append(str(line))
                                        try:
                                            self.__threadLock.acquire()
                                            self._evt_cb(self.rx_evt_results)
                                            self.__threadLock.release()
                                        except:
                                            pass
                                        self.rx_evt_results = []

                    if str.encode('{"S') in self.rx_buffer and self.__saveScanRsp:
                        if self._scan_cb != None:
                            decoded_result = self.rx_buffer.decode("utf-8", "ignore")
                            decoded_resultList = []
                            decoded_resultList = decoded_result.split("\r\n")
                            for line in decoded_resultList:
                                if line:
                                    if ('{"S') in line and not ('{"SE') in line:
                                        self.rx_scanning_results.append(str(line))
                                        try:
                                            self.__threadLock.acquire()
                                            self._scan_cb(self.rx_scanning_results)
                                            self.__threadLock.release()
                                        except:
                                            pass
                                        self.rx_scanning_results = []

                    if (
                        str.encode("VERBOSE ON") in self.rx_buffer
                        and not self.__cmdDone
                    ):
                        self.__threadLock.acquire()
                        self.rx_response.append(self.rx_buffer)
                        self.__cmdDone = True
                        self.__threadLock.release()

                    if str.encode("{") in self.rx_buffer and not self.__cmdDone:
                        care_result = self.rx_buffer.decode("utf-8", "ignore")
                        care_resultList = care_result.split("\r\n")
                        for line in care_resultList:
                            changeRoleCmd = False
                            role = ""
                            if line:
                                if (
                                    ('{"C"') in line
                                    or ('{"A"') in line
                                    or ('{"R"') in line
                                    or ('{"E"') in line
                                ):
                                    if '"gap_role"' in line:
                                        jsonStr = json.loads(line)
                                        self.status.role = jsonStr["gap_role"]

                                    if '"hw"' in line:
                                        jsonStr = json.loads(line)
                                        if "DA14683" in jsonStr["hw"]:
                                            self.dongleTypeStd = True
                                            if '"fwVer"' in line:
                                                jsonStr = json.loads(line)
                                                self.fwVersion = jsonStr["fwVer"]
                                                if len(self.fwVersion) >= 5:
                                                    checkVer = self.fwVersion[0:5]
                                                    checkVer = checkVer.replace(".", "")
                                                    try:
                                                        checkVer = int(checkVer)
                                                    except:
                                                        raise self.BleuIOException(
                                                            "Cannot read firmware version!"
                                                        )
                                                    if checkVer < 221:
                                                        raise self.BleuIOException(
                                                            "BleuIO firmware version is not supported by the BleuIO Python Library!\nSupported version is >= 2.2.1."
                                                        )

                                    if '"connected"' in line and not '"action"' in line:
                                        jsonStr = json.loads(line)
                                        self.__threadLock.acquire()
                                        self.status.isConnected = jsonStr["connected"]
                                        self.__threadLock.release()

                                    if (
                                        '"advertising"' in line
                                        and not '"action"' in line
                                    ):
                                        jsonStr = json.loads(line)
                                        self.__threadLock.acquire()
                                        self.status.isAdvertising = jsonStr[
                                            "advertising"
                                        ]
                                        self.__threadLock.release()

                                    if not changeRoleCmd and "AT+PERIPHERAL" in line:
                                        changeRoleCmd = True
                                        role = PERIPHERAL
                                    if not changeRoleCmd and "AT+DUAL" in line:
                                        changeRoleCmd = True
                                        role = DUAL
                                    if not changeRoleCmd and "AT+CENTRAL" in line:
                                        changeRoleCmd = True
                                        role = CENTRAL
                                    if changeRoleCmd and '"err":0,"' in line:
                                        self.__threadLock.acquire()
                                        self.status.role = role
                                        self.__threadLock.release()
                                    self.__threadLock.acquire()
                                    self.rx_response.append(line.encode())
                                    self.__threadLock.release()
                        if b'{"E":' in self.rx_buffer:
                            self.__threadLock.acquire()
                            self.__cmdDone = True
                            self.__threadLock.release()
                    if self._debug:
                        try:
                            print("debug(rx_buffer): " + str(self.rx_buffer))
                        except Exception:
                            pass
                    self.rx_buffer = b""
            except serial.SerialException as e:
                print("exception: " + str(e))
                self.alive = False
                sys.exit(1)

    def register_scan_cb(self, callback):
        """Registers callback function for recieving scan results.

        :param callback: Function with a data parameter. Function will be called for every scan result.
        :type callback : hex str
        :returns: Scan results.
        :rtype: str
        """
        self._scan_cb = callback

    def register_evt_cb(self, callback):
        """Registers callback function for recieving events.

        :param callback: Function with a data parameter. Function will be called for every event.
        :type callback : hex str
        :returns: Event results.
        :rtype: str
        """
        self.__saveEvtRsp = True
        self._evt_cb = callback

    def unregister_scan_cb(self):
        """Unregister the callback function for recieving scan results."""
        self._scan_cb = None

    def unregister_evt_cb(self):
        """Unregister the callback function for recieving events."""
        self.__saveEvtRsp = False
        self._evt_cb = None

    def send_command(self, cmd):
        if not self._serial.is_open:
            raise self.BleuIOException("Port to BleuIO is not open!")

        if self.status.isSPSStreamOn and cmd != "esc":
            self._serial.write(cmd.encode())
            self.rx_response.append(str('{"A":"","err": 0, "status": "ok"}').encode())
            return self.rx_response
        else:
            if self._debug:
                print("send_command: " + cmd)
            self.rx_response = []
            self._serial.reset_output_buffer()
            if self.status.isScanning and cmd != "stop":
                self.rx_response.append(
                    str(
                        '{"A":"","err": 1, "status": "Cannot send any commands while scanning."}'
                    ).encode()
                )
                self.cmd = ""
                return self.rx_response
            self.__cmdDone = False
            if cmd.__eq__("stop"):
                if self.status.isScanning:
                    self._serial.write("\x03".encode())
                    self.cmd = ""
                    while not self.__cmdDone:
                        pass
                    return self.rx_response
                else:
                    self._serial.write("\x03".encode())
                    self.cmd = ""
                    self.__cmdDone = True
                    self.rx_response.append(
                        str('{"A":"","err": 1, "status": "Not Scanning."}').encode()
                    )
                    return self.rx_response

            elif cmd.__eq__("esc"):
                if self.status.isSPSStreamOn:
                    self._serial.write("\x1B".encode())
                    self.cmd = ""
                    while not self.__cmdDone:
                        pass
                    return self.rx_response
                else:
                    self._serial.write("\x1B".encode())
                    self.cmd = ""
                    self.__cmdDone = True
                    self.rx_response.append(
                        str('{"A":"","err": 1, "status": "Not Streaming."}').encode()
                    )
                    return self.rx_response
            else:
                if not cmd == "":
                    if self._debug:
                        print("serial.write: " + cmd)
                    self._serial.write(cmd.encode())
                    self._serial.write(str.encode("\r"))
                    self.cmd = ""
            while not self.__cmdDone:
                pass
            return self.rx_response

    def __at(self):
        return self.send_command("AT")

    def __ata(self, isOn):

        if isOn:
            return self.send_command("ATA1")
        if not isOn:
            return self.send_command("ATA0")

    def __atb(self):
        return self.send_command("ATB")

    def __atasps(self, isOn):

        if isOn:
            return self.send_command("ATASPS1")
        if not isOn:
            return self.send_command("ATASPS0")

    def __atassm(self, isOn):

        if isOn:
            return self.send_command("ATASSM1")
        if not isOn:
            return self.send_command("ATASSM0")

    def __atassn(self, isOn):

        if isOn:
            return self.send_command("ATASSN1")
        if not isOn:
            return self.send_command("ATASSN0")

    def __atds(self, isOn):

        if isOn:
            return self.send_command("ATDS1")
        if not isOn:
            return self.send_command("ATDS0")

    def __ate(self, isOn):

        if isOn:
            return self.send_command("ATE1")
        if not isOn:
            return self.send_command("ATE0")

    def __ates(self, isOn):

        if isOn:
            return self.send_command("ATES=1")
        if not isOn:
            return self.send_command("ATES=0")

    def __ati(self):
        return self.send_command("ATI")

    def __atr(self):
        return self.send_command("ATR")

    def __atsat(self, isOn):

        if isOn:
            return self.send_command("ATSAT1")
        if not isOn:
            return self.send_command("ATSAT0")

    def __atsiv(self, isOn):

        if isOn:
            return self.send_command("ATSIV1")
        if not isOn:
            return self.send_command("ATSIV0")

    def __atsra(self, isOn):

        if isOn:
            return self.send_command("ATSRA1")
        if not isOn:
            return self.send_command("ATSRA0")

    def __at_advextparam(
        self,
        handle,
        disc_mode,
        prop,
        min_intv,
        max_intv,
        chnl_map,
        local_addr_type,
        filt_pol,
        tx_pwr,
        pri_phy,
        sec_max_evt_skip,
        sec_phy,
        sid,
        scan_req_noti,
        peer_addr_type,
        peer_addr,
    ):
        enable_scan_req_notification = "0"
        if not (
            handle == ""
            and disc_mode == ""
            and prop == ""
            and min_intv == ""
            and max_intv == ""
            and chnl_map == ""
            and local_addr_type == ""
            and filt_pol == ""
            and tx_pwr == ""
            and pri_phy == ""
            and sec_max_evt_skip == ""
            and sec_phy == ""
            and sid == ""
            and scan_req_noti == ""
            and peer_addr_type == ""
            and peer_addr == ""
        ):
            if scan_req_noti:
                enable_scan_req_notification = "1"
            if not peer_addr_type == "" and not peer_addr == "":
                return self.send_command(
                    "AT+ADVEXTPARAM="
                    + str(handle)
                    + "="
                    + str(disc_mode)
                    + "="
                    + str(prop)
                    + "="
                    + str(min_intv)
                    + "="
                    + str(max_intv)
                    + "="
                    + str(chnl_map)
                    + "="
                    + str(local_addr_type)
                    + "="
                    + str(filt_pol)
                    + "="
                    + str(tx_pwr)
                    + "="
                    + str(pri_phy)
                    + "="
                    + str(sec_max_evt_skip)
                    + "="
                    + str(sec_phy)
                    + "="
                    + str(sid)
                    + "="
                    + str(enable_scan_req_notification)
                    + "="
                    + str(peer_addr_type)
                    + "="
                    + str(peer_addr)
                )
            else:
                return self.send_command(
                    "AT+ADVEXTPARAM="
                    + str(handle)
                    + "="
                    + str(disc_mode)
                    + "="
                    + str(prop)
                    + "="
                    + str(min_intv)
                    + "="
                    + str(max_intv)
                    + "="
                    + str(chnl_map)
                    + "="
                    + str(local_addr_type)
                    + "="
                    + str(filt_pol)
                    + "="
                    + str(tx_pwr)
                    + "="
                    + str(pri_phy)
                    + "="
                    + str(sec_max_evt_skip)
                    + "="
                    + str(sec_phy)
                    + "="
                    + str(sid)
                    + "="
                    + str(enable_scan_req_notification)
                )
        else:
            return self.send_command("AT+ADVEXTPARAM")

    def __at_advextstart(self, handle, advdata, scan_rsp_data):

        if advdata == "":
            advdata = "-"
        if scan_rsp_data == "":
            scan_rsp_data = "-"
        return self.send_command(
            "AT+ADVEXTSTART="
            + str(handle)
            + "="
            + str(advdata)
            + "="
            + str(scan_rsp_data)
        )

    def __at_advextupd(self, handle, advdata, scan_rsp_data):

        if advdata == "":
            advdata = "-"
        if scan_rsp_data == "":
            scan_rsp_data = "-"
        return self.send_command(
            "AT+ADVEXTUPD="
            + str(handle)
            + "="
            + str(advdata)
            + "="
            + str(scan_rsp_data)
        )

    def __at_advdata(self, advData):

        if not advData == "":
            return self.send_command("AT+ADVDATA=" + advData)
        elif advData == "":
            return self.send_command("AT+ADVDATA")

    def __at_advdatai(self, advData):

        return self.send_command("AT+ADVDATAI=" + advData)

    def __at_advstart(self, conn_type, intv_min, intv_max, timer):

        if not (conn_type == "" and intv_min == "" and intv_max == "" and timer == ""):
            return self.send_command(
                "AT+ADVSTART="
                + str(conn_type)
                + ";"
                + str(intv_min)
                + ";"
                + str(intv_max)
                + ";"
                + str(timer)
                + ";"
            )
        else:
            return self.send_command("AT+ADVSTART")

    def __at_advstop(self):

        return self.send_command("AT+ADVSTOP")

    def __at_advresp(self, respData):

        if respData == "":
            return self.send_command("AT+ADVRESP")
        else:
            return self.send_command("AT+ADVRESP=" + respData)

    def __at_auto_exec(self, cmds):

        if cmds == "":
            return self.send_command("AT+AUTOEXEC")
        else:
            return self.send_command("AT+AUTOEXEC=" + cmds)

    def __at_cancel_connect(self):

        return self.send_command("AT+CANCELCONNECT")

    def __at_central(self):

        return self.send_command("AT+CENTRAL")

    def __at_clearnoti(self, handle):

        return self.send_command("AT+CLEARNOTI=" + handle)

    def __at_clearindi(self, handle):

        return self.send_command("AT+CLEARINDI=" + handle)

    def __at_client(self):

        return self.send_command("AT+CLIENT")

    def __at_clrautoexec(self):

        return self.send_command("AT+CLRAUTOEXEC")

    def __at_clruoi(self):

        return self.send_command("AT+CLRUOI")

    def __at_connectbond(self, addr):
        return self.send_command("AT+CONNECTBOND=" + str(addr))

    def __at_connparam(self, intv_min, intv_max, slave_latency, sup_timeout):

        adv_params = False
        if intv_min:
            if intv_max:
                if slave_latency:
                    if sup_timeout:
                        adv_params = True
                        return self.send_command(
                            "AT+CONNPARAM="
                            + intv_min
                            + "="
                            + intv_max
                            + "="
                            + slave_latency
                            + "="
                            + sup_timeout
                        )
        if not adv_params:
            return self.send_command("AT+CONNPARAM")

    def __at_connscanparam(self, scan_intv, scan_win):
        if not (scan_intv == "" and scan_intv == ""):
            return self.send_command(
                "AT+CONNSCANPARAM=" + str(scan_intv) + "=" + str(scan_win)
            )
        else:
            return self.send_command("AT+CONNSCANPARAM")

    def __at_devicename(self, name):

        if name == "":
            return self.send_command("AT+DEVICENAME")
        else:
            return self.send_command("AT+DEVICENAME=" + name)

    def __at_dis(self):

        return self.send_command("AT+DIS")

    def __at_dual(self):

        return self.send_command("AT+DUAL")

    def __at_enter_passkey(self, passkey):

        return self.send_command("AT+ENTERPASSKEY=" + passkey)

    def __at_findscandata(self, scandata, timeout=0):

        self.rx_scanning_results = []
        if timeout == 0:
            return self.send_command("AT+FINDSCANDATA=" + scandata)
        else:
            return self.send_command("AT+FINDSCANDATA=" + scandata + "=" + str(timeout))

    def __at_frssi(self, rssi):

        return self.send_command("AT+FRSSI=" + rssi)

    def __at_gapaddrtype(self, addr_type):

        if addr_type == "":
            return self.send_command("AT+GAPADDRTYPE")
        else:
            return self.send_command("AT+GAPADDRTYPE=" + str(addr_type))

    def __at_gapconnect(self, addr, intv_min, intv_max, slave_latency, sup_timeout):

        adv_params = False
        if intv_min:
            if intv_max:
                if slave_latency:
                    if sup_timeout:
                        adv_params = True
                        return self.send_command(
                            "AT+GAPCONNECT="
                            + addr
                            + "="
                            + intv_min
                            + ":"
                            + intv_max
                            + ":"
                            + slave_latency
                            + ":"
                            + sup_timeout
                            + ":"
                        )
        if not adv_params:
            return self.send_command("AT+GAPCONNECT=" + addr)

    def __at_gapdisconnect(self):

        return self.send_command("AT+GAPDISCONNECT")

    def __at_gapdisconnectall(self):

        return self.send_command("AT+GAPDISCONNECTALL")

    def __at_gapiocap(self, io_cap):

        if io_cap == "":
            return self.send_command("AT+GAPIOCAP")
        else:
            return self.send_command("AT+GAPIOCAP=" + io_cap)

    def __at_gappair(self, bond):

        if bond:
            return self.send_command("AT+GAPPAIR=BOND")
        else:
            return self.send_command("AT+GAPPAIR")

    def __at_gapscan(self, timeout):

        self.rx_scanning_results = []
        if not timeout == 0:
            return self.send_command("AT+GAPSCAN=" + str(timeout))
        if timeout == 0:
            return self.send_command("AT+GAPSCAN")

    def __at_gapunpair(self, addr):

        if addr == "":
            return self.send_command("AT+GAPUNPAIR")
        else:
            return self.send_command("AT+GAPUNPAIR=" + addr)

    def __at_gapstatus(self):

        return self.send_command("AT+GAPSTATUS")

    def __at_gattcread(self, handle):

        return self.send_command("AT+GATTCREAD=" + handle)

    def __at_gattcwrite(self, handle, data):

        return self.send_command("AT+GATTCWRITE=" + handle + " " + data)

    def __at_gattcwriteb(self, handle, data):

        return self.send_command("AT+GATTCWRITEB=" + handle + " " + data)

    def __at_gattcwritewr(self, handle, data):

        return self.send_command("AT+GATTCWRITEWR=" + handle + " " + data)

    def __at_gattcwritewrb(self, handle, data):

        return self.send_command("AT+GATTCWRITEWRB=" + handle + " " + data)

    def __at_getbond(self):

        return self.send_command("AT+GETBOND")

    def __at_get_services(self):

        return self.send_command("AT+GETSERVICES")

    def __at_get_services_only(self):

        return self.send_command("AT+GETSERVICESONLY")

    def __at_get_service_details(self, handle):

        return self.send_command("AT+GETSERVICEDETAILS=" + handle)

    def __at_get_conn(self):

        return self.send_command("AT+GETCONN")

    def __at_get_mac(self):

        return self.send_command("AT+GETMAC")

    def __at_indi(self):

        return self.send_command("AT+INDI")

    def __at_led(self, isOn, toggle, on_period, off_period):

        if not isOn == "":
            if isOn:
                return self.send_command("AT+LED=1")
            else:
                return self.send_command("AT+LED=0")

        if not toggle == "":
            if not on_period == "" and not off_period == "":
                return self.send_command(
                    "AT+LED=T=" + str(on_period) + "=" + str(off_period)
                )
            else:
                return self.send_command("AT+LED=T")
        return self.send_command("AT+LED=0")

    def __at_noti(self):

        return self.send_command("AT+NOTI")

    def __at_numcompa(self, auto_accept):

        if auto_accept == "0":
            return self.send_command("AT+NUMCOMPA=0")
        elif auto_accept == "1":
            return self.send_command("AT+NUMCOMPA=1")
        else:
            return self.send_command("AT+NUMCOMPA")

    def __at_peripheral(self):

        return self.send_command("AT+PERIPHERAL")

    def __at_scantarget(self, addr):

        return self.send_command("AT+SCANTARGET=" + addr)

    def __at_sec_lvl(self, sec_lvl):

        if sec_lvl == "":
            return self.send_command("AT+SECLVL")
        else:
            return self.send_command("AT+SECLVL=" + sec_lvl)

    def __at_server(self):

        return self.send_command("AT+SERVER")

    def __at_set_dis(self, manuf, model_num, serial_num, hw_rev, fw_rev, sw_rev):

        return self.send_command(
            "AT+SETDIS="
            + manuf
            + "="
            + model_num
            + "="
            + serial_num
            + "="
            + hw_rev
            + "="
            + fw_rev
            + "="
            + sw_rev
        )

    def __at_set_noti(self, handle):

        return self.send_command("AT+SETNOTI=" + handle)

    def __at_set_indi(self, handle):

        return self.send_command("AT+SETINDI=" + handle)

    def __at_set_passkey(self, passkey):

        if passkey == "":
            return self.send_command("AT+SETPASSKEY")
        else:
            return self.send_command("AT+SETPASSKEY=" + passkey)

    def __at_set_uoi(self, uoi_str):

        return self.send_command("AT+SETUOI=" + uoi_str)

    def __at_show_rssi(self, rssi):

        if rssi:
            return self.send_command("AT+SHOWRSSI=1")
        else:
            return self.send_command("AT+SHOWRSSI=0")

    def __at_spssend(self, data=""):

        if not self.status.isSPSStreamOn:
            if data == "":
                return self.send_command("AT+SPSSEND")
            if not data == "":
                return self.send_command("AT+SPSSEND=" + data)
        else:
            return self.send_command(data)

    def __at_target_conn(self, conn_idx):

        if conn_idx == "":
            return self.send_command("AT+TARGETCONN")
        else:
            return self.send_command("AT+TARGETCONN=" + conn_idx)

    def __at_txpwr(self, air_op="", tx_pwr=""):

        if not air_op == "" and not tx_pwr == "":
            return self.send_command("AT+TXPWR=" + str(air_op) + "=" + str(tx_pwr))
        else:
            return self.send_command("AT+TXPWR")

    def __at_scanfilter(self, sftype, value):
        if sftype == None and value == "":
            return self.send_command("AT+SCANFILTER")
        else:
            if value == "":
                return self.send_command("AT+SCANFILTER=" + str(sftype))
            else:
                return self.send_command("AT+SCANFILTER=" + str(sftype) + "=" + value)

    def __at_scanparam(self, mode, type, scan_intv, scan_win, filt_dupl):
        filter_duplicate = "0"
        if not (
            mode == ""
            and type == ""
            and scan_intv == ""
            and scan_intv == ""
            and filt_dupl == ""
        ):
            if filt_dupl:
                filter_duplicate = "1"

            return self.send_command(
                "AT+SCANPARAM="
                + str(mode)
                + "="
                + str(type)
                + "="
                + str(scan_intv)
                + "="
                + str(scan_win)
                + "="
                + str(filter_duplicate)
            )
        else:
            return self.send_command("AT+SCANPARAM")

    def __at_customservice(self, idx, cstype, value):
        if idx == None and cstype == None and value == "":
            return self.send_command("AT+CUSTOMSERVICE")
        else:
            return self.send_command(
                "AT+CUSTOMSERVICE=" + str(idx) + "=" + str(cstype) + "=" + value
            )

    def __at_customservice_start(self):
        return self.send_command("AT+CUSTOMSERVICESTART")

    def __at_customservice_stop(self):
        return self.send_command("AT+CUSTOMSERVICESTOP")

    def __at_customservice_reset(self):
        return self.send_command("AT+CUSTOMSERVICERESET")

    def __at_suota_start(self):
        return self.send_command("AT+SUOTASTART")

    def __at_suota_stop(self):
        return self.send_command("AT+SUOTASTOP")

    def __help(self):

        return self.send_command("--H")

    def __stop_scan(self):

        return self.send_command("stop")

    def __stop_sps(self):

        return self.send_command("esc")

    def exit_bootloader(self):
        """[BleuIO Pro Only] Exits bootloader.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        self._serial.write("QUIT\r".encode())
        response = self.BleuIORESP()
        response.Cmd = json.loads('{"C":0,"cmd":"QUIT"}')
        response.Ack = json.loads('{"A":0,"err":0,"errMsg":"ok"}')
        response.End = json.loads('{"E":0,"nol":4}')
        return response

    def stop_scan(self):
        """Stops any type of scan.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__stop_scan()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def stop_sps(self):
        """Stops SPS Stream-mode.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__stop_sps()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at(self):
        """Basic AT-Command.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def ata(self, isOn):
        """Shows/hides ascii values from notification/indication/read responses.

        :param isOn: True=On, False=Off
        :type isOn : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__ata(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atb(self):
        """[BleuIO Pro Only] Starts bootloader.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        self._serial.write("ATB\r".encode())
        response = self.BleuIORESP()
        response.Cmd = json.loads('{"C":0,"cmd":"ATB"}')
        response.Ack = json.loads('{"A":0,"err":0,"errMsg":"ok"}')
        response.End = json.loads('{"E":0,"nol":4}')

        return response

    def at_advextparam(
        self,
        handle="",
        disc_mode="",
        prop="",
        min_intv="",
        max_intv="",
        chnl_map="",
        local_addr_type="",
        filt_pol="",
        tx_pwr="",
        pri_phy="",
        sec_max_evt_skip="",
        sec_phy="",
        sid="",
        scan_req_noti="",
        peer_addr_type="",
        peer_addr="",
    ):
        """[BleuIO Pro Only] Sets advertising parameters for extended advertising. Needs to be set before starting extended advertising.

        :param handle: str
        :param disc_mode: str
        :param prop: str
        :param min_intv: str
        :param max_intv: str
        :param chnl_map: str
        :param local_addr_type: str
        :param filt_pol: str
        :param tx_pwr: str
        :param pri_phy: str
        :param sec_max_evt_skip: str
        :param sec_phy: str
        :param sid: str
        :param scan_req_noti: bool
        :param peer_addr_type: str
        :param peer_addr: str

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_advextparam(
            handle,
            disc_mode,
            prop,
            min_intv,
            max_intv,
            chnl_map,
            local_addr_type,
            filt_pol,
            tx_pwr,
            pri_phy,
            sec_max_evt_skip,
            sec_phy,
            sid,
            scan_req_noti,
            peer_addr_type,
            peer_addr,
        )
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_advextstart(self, handle, advdata="", scan_rsp_data=""):
        """[BleuIO Pro Only] Sets extended advertising data and/or scan response data and starts extended advertising.

        :param handle: str
        :param advdata: str
        :param scan_rsp_data: str

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_advextstart(handle, advdata, scan_rsp_data)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_advextupd(self, handle, advdata="", scan_rsp_data=""):
        """[BleuIO Pro Only] Sets extended advertising data and/or scan response data when advertising.

        :param handle: str
        :param advdata: str
        :param scan_rsp_data: str

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_advextupd(handle, advdata, scan_rsp_data)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def ates(self, isOn):
        """[BleuIO Pro Only] Toggles showing extended scan results on/off. Off by default.

        :param isOn: True=On, False=Off
        :type isOn : bool

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__ates(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_led(self, isOn="", toggle="", on_period="", off_period=""):
        """[BleuIO Pro Only] Controls the LED.

        :param isOn: bool
        :param toggle: bool
        :param on_period: str
        :param off_period: str

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_led(isOn, toggle, on_period, off_period)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_txpwr(self, air_op="", tx_pwr=""):
        """[BleuIO Pro Only] Sets the TX output effect for advertsing, scan and/or initiate air operation.

        :param air_op: str
        :param tx_pwr: str

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_txpwr(air_op, tx_pwr)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atasps(self, isOn):
        """Toggle between ascii (Off) and hex responses (On) received from SPS.

        :param isOn: True=On, False=Off
        :type isOn : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__atasps(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atassm(self, isOn):
        """Turns on/off showing Manufacturing Specific ID (Company ID), if present, in scan results from AT+GAPSCAN, AT+FINDSCANDATA and AT+SCANTARGET scans. (Off per default).

        :param isOn: True=On, False=Off
        :type isOn : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__atassm(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atassn(self, isOn):
        """Turns on/off showing device names, if present, in scan results from AT+FINDSCANDATA and AT+SCANTARGET scans. (Off per default).

        :param isOn: True=On, False=Off
        :type isOn : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__atassn(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atds(self, isOn):
        """Turns auto discovery of services when connecting on/off.

        :param isOn: (boolean) True=On, False=Off
        :type isOn : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__atds(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def ate(self, isOn):
        """Turns Echo on/off.

        :param isOn: (boolean) True=On, False=Off
        :type isOn : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__ate(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def ati(self):
        """Device information query.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__ati()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atr(self):
        """Trigger platform reset.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__atr()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atsat(self, isOn):
        """Turns on/off showing address types in scan results from AT+FINDSCANDATA and AT+SCANTARGET scans.
        (Off per default).

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__atsat(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atsiv(self, isOn):
        """Turns showing verbose scan result index on/off. (Off per default).

        :param isOn: True=On, False=Off
        :type isOn : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__atsiv(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def atsra(self, isOn):
        """Turns showing resolved addr in scan results on/off. (Off per default).

        :param isOn: True=On, False=Off
        :type isOn : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__atsra(isOn)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_advdata(self, advdata=""):
        """Sets or queries the advertising data.

        :param: Sets advertising data. If left empty it will query what advdata is set. Format: xx:xx:xx:xx:xx.. (max 31 bytes)
        :type advdata: hex str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_advdata(advdata)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_advdatai(self, advdata):
        """Sets advertising data in a way that lets it be used as an iBeacon.
        Format = (UUID)(MAJOR)(MINOR)(TX)
        Example: at_advdatai("5f2dd896-b886-4549-ae01-e41acd7a354a0203010400")

        :param: Sets advertising data in iBeacon format. If left empty it will query what advdata is set
        :type advdata: hex str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_advdatai(advdata)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_advstart(self, conn_type="", intv_min="", intv_max="", timer=""):
        """Starts advertising with default settings if no params.
        With params: Starts advertising with <conn_type><intv_min><intv_max><timer>.

        :param: Starts advertising with default settings.
        :type conn_type: str
        :type intv_min: str
        :type intv_max: str
        :type timer: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_advstart(conn_type, intv_min, intv_max, timer)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_advstop(self):
        """Stops advertising.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_advstop()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_advresp(self, respData=""):
        """Sets or queries scan response data. Data must be provided as hex string.

        :param: Sets scan response data. If left empty it will query what advdata is set. Format: xx:xx:xx:xx:xx.. (max 31 bytes)
        :type respData: hex str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_advresp(respData)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_autoexec(self, cmds=""):
        """Sets or displays up to 10 commands that will be run upon the BleuIO starting up. Max command lenght is currently set at 255 characters.

        :param: Sets commands. If left empty it will query set commands.
        :type cmds: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_auto_exec(cmds)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_cancel_connect(self):
        """While in Central Mode, cancels any ongoing connection attempts.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_cancel_connect()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_central(self):
        """Sets the device Bluetooth role to central role.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_central()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_clearnoti(self, handle):
        """Disables notification for selected characteristic.

        :param handle: hex str format: XXXX
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_clearnoti(handle)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_clearindi(self, handle):
        """Disables indication for selected characteristic.

        :param handle: hex str format: XXXX
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_clearindi(handle)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_client(self):
        """Sets the device role towards the targeted connection to client. Only in dual role.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_client()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_clrautoexec(self):
        """Clear any commands in the auto execute (AUTOEXEC) list.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_clrautoexec()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_clruoi(self):
        """Clear any set Unique Organization ID.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_clruoi()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_connectbond(self, addr):
        """Scan for and initiates a connection with a selected bonded device. Works even if the peer bonded device is advertising with a Private Random Resolvable Address.

        :param addr: hex str format: XX:XX:XX:XX:XX:XX
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_connectbond(addr)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_connparam(self, intv_min="", intv_max="", slave_latency="", sup_timeout=""):
        """Sets or displays preferred connection parameters. When run while connected will update connection parameters on the current target connection.

        :param intv_min: str
        :param intv_max: str
        :param slave_latency: str
        :param sup_timeout: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_connparam(intv_min, intv_max, slave_latency, sup_timeout)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_connscanparam(self, scan_intv="", scan_win=""):
        """Set or queries the connection scan window and interval used.

        :param scan_intv: str
        :param scan_win: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_connscanparam(scan_intv, scan_win)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_devicename(self, name=""):
        """Gets or sets the device name.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_devicename(name)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_dis(self):
        """Shows the DIS Service info and if the DIS info is locked in or can be changed.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_dis()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_dual(self):
        """Sets the device Bluetooth role to dual role.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_dual()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_enter_passkey(self, passkey):
        """Respond to Passkey request. When faced with this message: BLE_EVT_GAP_PASSKEY_REQUEST use this command to enter
        the 6-digit passkey to continue the pairing request.

        :param passkey: str: six-digit number string "XXXXXX"
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_enter_passkey(passkey)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_findscandata(self, scandata="", timeout=0):
        """Scans for all advertising/response data which contains the search params.

        :param scandata: Hex string to filter the advertising/scan response data. Can be left blank to scan for everything. Format XXXX..
        :type scandata: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        scandata = scandata.upper()
        care = self.__at_findscandata(scandata, timeout)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)
        self.__saveScanRsp = True
        if self._scan_cb == None:
            self.send_command("stop")
            self.__saveScanRsp = False

        return response

    def at_frssi(self, rssi):
        """Filters scan results, showing only results with <max_rssi> value or lower.

        :param rssi: RSSI value. Must be negative. eg. -67
        :type rssi: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_frssi(rssi)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gapaddrtype(self, addr_type=""):
        """Change device Address Type or queries device Address Type.

        :param addr_type: Range: 1-5. If left blank queries current Address Type.
        :type addr_type: int
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gapaddrtype(addr_type)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gapconnect(
        self,
        addr,
        intv_min="",
        intv_max="",
        slave_latency="",
        sup_timeout="",
    ):
        """Initiates a connection with a specific slave device. [<addr_type>]<address>=<intv_min>:<intv_max>:<slave_latency>:<sup_timeout>

        :param addr: hex str format: [X]XX:XX:XX:XX:XX:XX
        :param intv_min: str
        :param intv_max: str
        :param slave_latency: str
        :param sup_timeout: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """

        care = self.__at_gapconnect(
            addr, intv_min, intv_max, slave_latency, sup_timeout
        )
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gapdisconnect(self):
        """Disconnects from a peer Bluetooth device.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gapdisconnect()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gapdisconnectall(self):
        """Disconnects from all peer Bluetooth devices.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gapdisconnectall()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gapiocap(self, io_cap=""):
        """Sets or queries what input and output capabilities the device has. Parameter is number between 0 to 4.

        :param io_cap: str: number
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gapiocap(io_cap)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gappair(self, bond=False):
        """Starts a pairing (bond=False) or bonding procedure (bond=True).

        :param bond: boolean
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gappair(bond)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gapunpair(self, addr_to_unpair=""):
        """Unpair paired devices if no parameters else unpair specific device. This will also remove the device bond data
        from BLE storage.
        Usable both when device is connected and when not.

        :param addr_to_unpair: hex str format: [X]XX:XX:XX:XX:XX:XX
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gapunpair(addr_to_unpair)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gapscan(self, timeout=0):
        """Starts a Bluetooth device scan with or without timer set in seconds.

        :param: if left empty it will scan indefinitely
        :param timeout: int (time in seconds)
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gapscan(timeout)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)
        self.__saveScanRsp = True
        if self._scan_cb == None:
            self.send_command("stop")
            self.__saveScanRsp = False

        return response

    def at_gapstatus(self):
        """Reports the Bluetooth role.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gapstatus()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gattcread(self, handle):
        """Read attribute of remote GATT server.

        :param handle: hex str format: XXXX
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gattcread(handle)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gattcwrite(self, handle, data):
        """Write attribute to remote GATT server in ASCII.

        :param handle: hex str format: XXXX
        :param data: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gattcwrite(handle, data)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gattcwriteb(self, handle, data):
        """Write attribute to remote GATT server in Hex.

        :param handle: hex str format: XXXX
        :param data: hex str format: XXXXXXX..
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gattcwriteb(handle, data)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gattcwritewr(self, handle, data):
        """Write, without response, attribute to remote GATT server in ASCII.

        :param handle: hex str format: XXXX
        :param data: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gattcwritewr(handle, data)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_gattcwritewrb(self, handle, data):
        """Write, without response, attribute to remote GATT server in Hex.

        :param handle: hex str format: XXXX
        :param data: hex str format: XXXXXXX..
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_gattcwritewrb(handle, data)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_getbond(self):
        """Displays all MAC address of bonded devices.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_getbond()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_get_conn(self):
        """Gets a list of currently connected devices along with their mac addresses and conn_idx.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_get_conn()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_get_mac(self):
        """Returns MAC address of the BleuIO device.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_get_mac()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_get_services(self):
        """Discovers all services of a peripheral and their descriptors and characteristics.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_get_services()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_get_servicesonly(self):
        """Discovers a peripherals services.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_get_services_only()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_get_service_details(self, handle):
        """Discovers all characteristics and descriptors of a selected service.

        :param handle: hex str format: XXXX
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_get_service_details(handle)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_indi(self):
        """Show list of set indication handles.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_indi()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_noti(self):
        """Show list of set notification handles.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_noti()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_numcompa(self, auto_accept="2"):
        """Used for accepting a numeric comparison authentication request (no params) or enabling/disabling auto-accepting
        numeric comparisons. auto_accept="0" = off, auto_accept="1" = on.

        :param auto_accept: str format: "0" or "1"
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_numcompa(auto_accept)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_peripheral(self):
        """Sets the device Bluetooth role to peripheral.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_peripheral()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_scantarget(self, addr):
        """Scan a target device. Displaying it's advertising and response data as it updates.

        :param addr: hex str format: "xx:xx:xx:xx:xx:xx"
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """

        care = self.__at_scantarget(addr)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)
        self.__saveScanRsp = True
        if self._scan_cb == None:
            self.send_command("stop")
            self.__saveScanRsp = False

        return response

    def at_sec_lvl(self, sec_lvl=""):
        """Sets or queries (no params) what minimum security level will be used when connected to other devices.

        :param sec_lvl:  str: string number between 0 and 4
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_sec_lvl(sec_lvl)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_server(self):
        """Sets the device role towards the targeted connection to server. Only in dual role.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_server()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_setdis(self, manuf, model_num, serial_num, hw_rev, fw_rev, sw_rev):
        """Sets the DIS Service info.

        :param manuf: str
        :param model_num: str
        :param serial_num: str
        :param hw_rev: str
        :param fw_rev: str
        :param sw_rev: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_set_dis(manuf, model_num, serial_num, hw_rev, fw_rev, sw_rev)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_set_noti(self, handle):
        """Enable notification for selected characteristic.

        :param handle: hex str format: XXXX
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_set_noti(handle)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_set_indi(self, handle):
        """Enable indication for selected characteristic.

        :param handle: hex str format: XXXX
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_set_indi(handle)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_set_passkey(self, passkey=""):
        """Setting or quering set passkey (no params) for passkey authentication.

        :param passkey: hex str format: "xxxxxx"
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_set_passkey(passkey)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_set_uoi(self, uoi_str):
        """Set Unique Organization ID. It will be stored in flash memory, and will persist through power cycles.
        If set, the Unique Organization ID string will be displayed in the ATI command's response. Will clear any previous set Unique Organization ID when set.
        Max length: 100 characters.

        :param uoi_str: str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_set_uoi(uoi_str)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

    def at_show_rssi(self, show_rssi=True):
        """Shows/hides RSSI in AT+FINDSCANDATA and AT+SCANTARGET scans.

        :param show_rssi: bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_show_rssi(show_rssi)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_spssend(self, data=""):
        """Send a message or data via the SPS profile.
        Without parameters it opens a stream for continiously sending data.

        :param: if left empty it will open Streaming mode
        :type data: str or None
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        response = self.BleuIORESP()
        care = self.__at_spssend(data)
        self.__parseRspIntoJSON(care, response)

        return response

    def at_target_conn(self, conn_idx=""):
        """Set or quering the connection index which is the targeted connection.

        :param conn_idx: connection index, format: xxxx
        :type conn_idx : hex str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_target_conn(conn_idx)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_scanfilter(self, sftype: str = None, value: str = ""):
        """Sets or queries the scanfilter. There are three types of scanfilter, filter by name, filter by uuid or by manufacturer specific ID.

        :param sftype: scan filter parameter type
        :type sftype : str
        :param value: value
        :type value : str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_scanfilter(sftype, value)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_scanparam(self, mode="", type="", scan_intv="", scan_win="", filt_dupl=""):
        """Set or queries the scan parameters used.

        :param mode: str
        :param type: str
        :param scan_intv: str
        :param scan_win: str
        :param filt_dupl: True=On, False=Off
        :type filt_dupl : bool
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_scanparam(mode, type, scan_intv, scan_win, filt_dupl)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_customservice(self, idx: int = None, cstype: str = None, value: str = ""):
        """Sets or queries Custom Service. Max 5 Characteristics can be added.
            Several values cannot be changed while connected/connecting or advertising.

        :param idx: service index
        :type idx : number
        :param cstype: custom service parameter type
        :type cstype : str
        :param value: value
        :type value : str
        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_customservice(idx, cstype, value)
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_customservice_start(self):
        """Starts the Custom Service based on the settings set by AT+CUSTOMSERVICE= Command.
            Cannot be started while connected/connecting or advertising

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_customservice_start()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_customservice_stop(self):
        """Stops the Custom Service.
            Cannot be changed while connected/connecting or advertising.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_customservice_stop()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_customservice_reset(self):
        """Stops the Custom Service and resets the Custom Service settings set by the AT+CUSTOMSERVICE= command to it's default values.
            Cannot be changed while connected/connecting or advertising..

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_customservice_reset()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_suota_start(self):
        """Enables the SUOTA Service and start the SUOTA Advertising.
           Cannot be started while connected/connecting or advertising.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_suota_start()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def at_suota_stop(self):
        """Disables the SUOTA Service and stops the SUOTA Advertising.
           Cannot be used while connected/connecting.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype: obj BleuIORESP
        """
        care = self.__at_suota_stop()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response

    def help(self):
        """Shows all AT-Commands.

        :returns: Object with 4 object properties: Cmd, Ack, Rsp and End. Each property contains a JSON object, except for Rsp which contains a list of JSON objects.
        :rtype obj BleuIORESP
        """
        care = self.__help()
        response = self.BleuIORESP()
        self.__parseRspIntoJSON(care, response)

        return response
