# (C) 2021 Smart Sensor Devices AB

import time
from datetime import datetime
import traceback

from bleuio_lib.bleuio_funcs import BleuIo

# Start // BleuIo(debug=True)
my_dongle = BleuIo(port="COM25")
my_dongle.start_daemon()
errorCounter = 0
num_loops = 30
loops_run = 0
file_name = "bleuio_lib_test_log.txt"
operator_name = "Emil Lindblom"
operator_location = "Smart Sensor Devices AB in Sollentuna"


def simplescan():
    # Saves the response (string list) of the ATI command to the status variable
    status = my_dongle.ati()
    for i in status:
        # Prints each line of status variable
        print(i)
        # Checks if dongle is in Peripheral
        # If it is it puts the dongle in Central Mode to allow scanning
        if i.__contains__("Peripheral"):
            setCentral = my_dongle.at_central()
            for l in setCentral:
                print(l)

    # Runs a scan for 4 seconds then prints out the results, line by line
    my_dongle.at_gapscan(4)
    scan_result = my_dongle.rx_scanning_results
    for y in scan_result:
        print(y)


def doesCmdRun(cmdRsp):
    global errorCounter
    print("".join(cmdRsp))
    if cmdRsp is None or cmdRsp == "" or cmdRsp == []:
        errorCounter = errorCounter + 1

purposleyWrong = []

# simplescan()

# Some more examples of almost every function
try:
    test_started = datetime.now()
    for i in range(0, num_loops):
        loops_run = loops_run + 1
        print(":" * 21)
        print("NEW LOOP! Number: " + str(loops_run))
        print(":" * 21)
        # print("purposleyWrong")
        # doesCmdRun(purposleyWrong)
        print("help")
        doesCmdRun((my_dongle.help()))
        print("ati")
        doesCmdRun((my_dongle.ati()))
        print("at_target_conn")
        doesCmdRun((my_dongle.at_target_conn()))
        print("at_get_conn")
        doesCmdRun((my_dongle.at_get_conn()))
        print("ata0")
        doesCmdRun((my_dongle.ata(False)))
        print("atds0")
        doesCmdRun((my_dongle.atds(False)))
        print("ata1")
        doesCmdRun((my_dongle.ata(True)))
        print("atds1")
        doesCmdRun((my_dongle.atds(True)))
        print("at_set_passkey=123456")
        doesCmdRun((my_dongle.at_set_passkey("123456")))
        print("at_set_passkey")
        doesCmdRun((my_dongle.at_set_passkey()))
        print("at_gapiocap=0")
        doesCmdRun((my_dongle.at_numcompa("0")))
        print("at_gapiocap=1")
        doesCmdRun((my_dongle.at_gapiocap("1")))

        print("at_sec_lvl=2")
        doesCmdRun((my_dongle.at_sec_lvl("2")))
        print("at_sec_lvl")
        doesCmdRun((my_dongle.at_sec_lvl()))
        print("at_sec_lvl=1")
        doesCmdRun((my_dongle.at_sec_lvl("1")))
        print("at_sec_lvl")
        doesCmdRun((my_dongle.at_sec_lvl()))
        print("at_gapiocap=2")
        doesCmdRun((my_dongle.at_gapiocap("2")))
        print("at_gapiocap")
        doesCmdRun((my_dongle.at_gapiocap()))
        print("at_gapiocap=1")
        doesCmdRun((my_dongle.at_gapiocap("1")))
        print("at_gapiocap")
        doesCmdRun((my_dongle.at_gapiocap()))

        print("at_peripheral")
        doesCmdRun((my_dongle.at_peripheral()))
        print("at")
        doesCmdRun((my_dongle.at()))
        print("ate(0)")
        doesCmdRun((my_dongle.ate(0)))
        print("ati")
        doesCmdRun((my_dongle.ati()))
        print("ate(1)")
        doesCmdRun((my_dongle.ate(1)))
        print("at_advdata")
        doesCmdRun((my_dongle.at_advdata()))
        print("at_advdata=04:09:43:41:54)")
        doesCmdRun((my_dongle.at_advdata("04:09:43:41:54")))
        print("at_advdatai(ebbaaf47-0e4f-4c65-8b08-dd07c98c41ca0000000000)")
        doesCmdRun((my_dongle.at_advdatai("ebbaaf47-0e4f-4c65-8b08-dd07c98c41ca0000000000")))
        print("at_advstart")
        doesCmdRun((my_dongle.at_advstart()))
        time.sleep(2)
        print("at_advstop")
        doesCmdRun((my_dongle.at_advstop()))
        print("at_advstart(1,500,600,20)")
        doesCmdRun((my_dongle.at_advstart("1", "500", "600", "20")))
        time.sleep(2)
        print("at_advstop")
        doesCmdRun((my_dongle.at_advstop()))
        print("at_central")
        doesCmdRun((my_dongle.at_central()))
        print("at_findscandata=")
        print("  ".join(my_dongle.at_findscandata("")))
        time.sleep(6)
        print("stop scan")
        doesCmdRun((my_dongle.stop_scan()))
        find = my_dongle.rx_scanning_results
        print("rx_scanning_results at_findscandata")
        print("=" * 21)
        for line in find:
            print(line)
        print("=" * 21)
        print("at_gapscan(5)")
        print(my_dongle.at_gapscan(5))
        find = my_dongle.rx_scanning_results
        print("rx_scanning_results at_gapscan(5) ")
        print("=" * 21)
        for line in find:
            print(line)
        print("=" * 21)
        print("=" * 21)
        print("at_gapscan")
        doesCmdRun((my_dongle.at_gapscan()))
        time.sleep(3)
        print("stop_scan")
        doesCmdRun((my_dongle.stop_scan()))
        gapscan = my_dongle.rx_scanning_results
        print("rx_scanning_results at_gapscan() ")
        print("=" * 21)
        for line in gapscan:
            print(line)
        print("=" * 21)
        print("at_gapstatus")
        doesCmdRun((my_dongle.at_gapstatus()))
        # doesCmdRun((my_dongle.at_numcompa())
        # doesCmdRun((my_dongle.at_enter_passkey("123456"))
        print("at_dual")
        doesCmdRun((my_dongle.at_dual()))
        print("at_gapconnect [0]40:48:FD:E5:2D:7C")
        doesCmdRun((my_dongle.at_gapconnect("[0]40:48:FD:E5:2D:7C",5)))
        time.sleep(5)
        print("at_gapdisconnect")
        doesCmdRun((my_dongle.at_gapdisconnect()))
        print("at_gapconnect [0]00:00:00:00:0D:D0")
        doesCmdRun((my_dongle.at_gapconnect("[0]00:00:00:00:0D:D0",5)))
        time.sleep(2)
        print("at_cancel_connect")
        doesCmdRun((my_dongle.at_cancel_connect()))
        time.sleep(2)
        print("at_gapconnect [0]40:48:FD:E5:2D:7C")
        doesCmdRun((my_dongle.at_gapconnect("[0]40:48:FD:E5:2D:7C",5)))
        time.sleep(5)
        print("at_get_services")
        doesCmdRun((my_dongle.at_get_services()))
        time.sleep(2)
        print("at_server")
        doesCmdRun((my_dongle.at_server()))
        time.sleep(2)
        print("at_client")
        doesCmdRun((my_dongle.at_client()))
        time.sleep(2)
        print("at_get_servicesonly")
        doesCmdRun((my_dongle.at_get_servicesonly()))
        time.sleep(2)
        print("at_gappair")
        doesCmdRun((my_dongle.at_gappair()))
        print("at_get_service_details")
        doesCmdRun((my_dongle.at_get_service_details("000b")))
        print("at_setnoti")
        doesCmdRun((my_dongle.at_setnoti("0021")))
        print("at_gattcread")
        doesCmdRun((my_dongle.at_gattcread("000b")))
        print("at_gattcwrite")
        doesCmdRun((my_dongle.at_gattcwrite("000d", "HEJ")))
        print("at_gattcwriteb")
        doesCmdRun((my_dongle.at_gattcwriteb("000d", "010101")))
        print("at_gattcwritewr")
        doesCmdRun((my_dongle.at_gattcwritewr("000d", "HEJ")))
        print("at_gattcwritewrb")
        doesCmdRun((my_dongle.at_gattcwritewrb("000d", "010101")))
        print("at_spssend")
        doesCmdRun((my_dongle.at_spssend("howdy")))
        print("at_spssend")
        doesCmdRun((my_dongle.at_spssend("howdy2")))
        print("at_gapdisconnectall")
        doesCmdRun((my_dongle.at_gapdisconnectall()))

    print("num of Errors: " + str(errorCounter))
    print("\r\n\r\n[PROGRAM FINISHED!]\r\n")
    now = datetime.now()  # Generating a timestamp
    timestamp = datetime.timestamp(now)  # Formatting the timestamp
    dt_object = datetime.fromtimestamp(timestamp)
    fo = open(file_name, "a")
    fo.write(
        str(dt_object)
        + " Test by: "
        + operator_name
        + " At: "
        + operator_location
        + "\r\n"
    )
    fo.write("-=:[SUCCESS]:=-\r\n")
    fo.write("Test Started: " + str(test_started) + "\r\n")
    fo.write("Errors: " + str(errorCounter) + "\r\n")
    fo.write("Loops run: " + str(loops_run) + " of " + str(num_loops) + "\r\n")
    fo.write(
        "---------------------------------------------------------------------------------------"
    )
    fo.write("\r\n")
    fo.close()
except:
    print("\r\n\r\n[PROGRAM CRASHED!]\r\n\r\nCrash rapport written in log.")
    error = traceback.format_exc()
    now = datetime.now()  # Generating a timestamp
    timestamp = datetime.timestamp(now)  # Formatting the timestamp
    dt_object = datetime.fromtimestamp(timestamp)
    fo = open(file_name, "a")
    fo.write(
        str(dt_object)
        + " Test by: "
        + operator_name
        + " At: "
        + operator_location
        + "\r\n"
    )
    fo.write("-=:[CRASH]:=-\r\n")
    fo.write("Test Started: " + str(test_started) + "\r\n")
    fo.write("Error info: " + error + "\r\n")
    fo.write("Loops run: " + str(loops_run) + " of " + str(num_loops) + "\r\n")
    fo.write(
        "---------------------------------------------------------------------------------------"
    )
    fo.write("\r\n")
    fo.close()
    my_dongle.atr()
