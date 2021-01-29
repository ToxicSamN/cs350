"""
    SammyShuck__wk5_MilestoneFour_Data_to_Dashboard.py

    Name: Sammy Shuck
    Date: 02/07/2021
    Class: CS350 Emerging Systems Architecture and Technology
    Term: 21EW3
    Assignment: 5-2 Final Project Milestone Four: Displaying the Data on a Dashboard

    This script will utilize a DHT sensor connected to a RaspberryPi.
    The temperature and humidity data will be collected every 60 seconds via the DHT sensor and
    saved to a file named data.json. This JSON data will then be used by canvasJS to display a
    dashboard.

    The JSON structure is specific:
    [
        [ ** temperature and humidity reading 1 **

            [unix timestamp, temperature in F],
            [unix timestamp, humidity in %]
        ],
        [ ** temperature and humidity reading 2 **
            [unix timestamp, temperature in F],
            [unix timestamp, humidity in %]
        ]
    ]
"""

# Import statements
from datetime import datetime
import grovepi
import json
import math
import multiprocessing
import os
import sys
import time

# different packages for universal windows platforms than with RPi
if sys.platform == 'uwp':
    import winrt_smbus as smbus

    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO

    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)


# Constant declaration
class PORT:
    """
    PORT object has constant definitions for the GrovePi riser board
    See https://www.dexterindustries.com/wp-content/uploads/2013/07/grovepi_pinout.png for more
    details.
    """

    class ANALOG:
        """
        ANALOG ports are defined as
        A0 = 0,
        A1 = 2,
        A2 = 3,
        GrovePi sockets A0,A1,A2 use the AD converter and support analogRead() values 0-1023
        Can only use analogRead() with A0, A1, A2 (aka D14, D15, D16)
        """

        A0 = 0
        A1 = 1
        A2 = 2

    class DIGITAL:
        """
        DIGITAL ports are defined as
        D2 = 2,
        D3 = 3,
        D4 = 4,
        D5 = 5,
        D6 = 6,
        D7 = 7,
        D8 = 8
        GrovePi sockets D2-D8 are digital and support 1-bit input/output, values 0-1,
        using digitalRead() and digitalWrite().

        GrovePi sockets D3,D5,D6 also support Pulse Width Modulation (PWM) which means you can
        write 8-bit values 0-255 with analogWrite().
        """

        D2 = 2
        D3 = 3
        D4 = 4
        D5 = 5
        D6 = 6
        D7 = 7
        D8 = 8

    class PWM:
        """
        Pulse Width Modulation (PWM) ports are defined as
        PWM1 = D3 = 3,
        PWM2 = D5 = 5,
        PWM3 = D6 = 6,

        GrovePi sockets D3,D5,D6 also support Pulse Width Modulation (PWM) which means you can
        write 8-bit values 0-255 with analogWrite()
        """

        PWM1 = 3
        PWM2 = 5
        PWM3 = 6


class DHT:
    BLUE = 0
    WHITE = 1


def CtoF(C):
    """
    Converts Celcius to Fahrenheit
    :param C: float valu in degrees Celsius
    :return: float value in degrees Fahrenheit
    """
    return float(float(C) * (9.0/5.0) + 32)


def main(out_q, errq):
    """
    Main program for collecting temperature and humidity data
    :param out_q: multiprocessing queue to send the collected weather data to
    :param errq: error queue for communicating exceptions to the parent process
    """

    weather_data = []  # list to store the weather data

    # establish a new LCD object
    dht_sensor_port = PORT.DIGITAL.D7  # dht sensor location D7
    dht_sensor_type = DHT.BLUE  # sensor type is blue, optionally it could be white

    while True:
        try:
            # collect the data from the sensor
            [temp, humidity] = grovepi.dht(dht_sensor_port, dht_sensor_type)
            if math.isnan(temp) is False and math.isnan(humidity) is False:
                # dict for preparation to send JSON to database
                unixtime = int(time.time()) * 1000  # for some strange reason canvasJS needs the extra 0's

                # configure the canvasJS JSON structure
                # [
                # 	[ ** temperature and humidity reading 1 **

                # 		[unix timestamp, temperature in F],
                # 		[unix timestamp, humidity in %]
                # 	],
                # 	[ ** temperature and humidity reading 2 **
                # 		[unix timestamp, temperature in F],
                # 		[unix timestamp, humidity in %]
                # 	]
                # ]
                weather_data.append([[unixtime, CtoF(temp)], [unixtime, humidity]])

                # send the updated weather data to be stored
                out_q.put(weather_data)

            # Program specification states to only collect data every 1 minute
            time.sleep(60)  # run every 1 minute

        except IOError as ioErr:
            errq.put_nowait(ioErr)
        except KeyboardInterrupt as kiErr:
            errq.put_nowait(kiErr)


def write_temp_to_database(in_q, errq):
    """
    Writes the temperature and humidity data to a database as JSON
    Expected to be ran as a separate process so the main program is
    not waiting for the file system or network I/O process to complete
    :param in_q: multiprocessing queue containing the weather data to offload
    :param errq: error queue for communicating exceptions to the parent process
    """
    try:
        # obtain output file
        outfile = os.getenv("CS350_OUTPUT", "data.json")
        # clear the contents of the data.json file initially
        with open(outfile, 'w+') as f:
            # this truncates the file and will replace any existing data in the file
            json.dump("", f)
            f.close()  # be good and proper

        print("Writing Weather Data to File " + outfile)
        while True:  # loop to continuously monitor the queue
            # retrieve the data from the queue
            # blocking queue until data is available
            temp_data = in_q.get()

            # ToDo: replace file storage with NoSQL database (Mongo, Couchbase, dynamoDB, etc)
            # write the data to a file
            # using /tmp/ as every *nix system has this dir available as R/W for everyone
            with open(outfile, 'w+') as f:
                # this truncates the file and will replace any existing data in the file
                json.dump(temp_data, f)
                f.close()  # be good and proper
    except IOError as ioErr:
        errq.put_nowait(ioErr)
    except BaseException as be:
        errq.put_nowait(be)


if __name__ == "__main__":
    try:
        # since dealing with file system IO processes it's better to
        # go ahead and have this IO bound process processed concurrently
        # with the temperature readings
        q_mgr = multiprocessing.Manager()
        fio_q = q_mgr.Queue(maxsize=5)
        err_q = q_mgr.Queue(maxsize=2)

        # create the file operation process
        fio_process = multiprocessing.Process(name="File_IO_Operation",
                                              target=write_temp_to_database,
                                              kwargs={'in_q': fio_q, 'errq': err_q})
        fio_process.start()
        # create the main process for collecting temp data and manipulating the lcd screen
        main_process = multiprocessing.Process(name="main",
                                               target=main,
                                               kwargs={'out_q': fio_q, 'errq': err_q})
        main_process.start()

        # monitor for state changes from the processes
        while True:
            if fio_process.is_alive() and main_process.is_alive():
                continue  # both processes are still running, continue

            # if only oen process is terminated, need to find the one still running.
            # be good and proper and release your resources, terminate the running process
            if not fio_process.is_alive():
                fio_process.terminate()
            if not main_process.is_alive():
                main_process.terminate()

            # retrieve the error from the queue
            err = err_q.get_nowait()
            raise err

    except BaseException as e:
        # capture all exceptions raised and exit the program
        print("Exception: " + str(e))
