"""
    SammyShuck__wk7_FinalProject_I.py

    Name: Sammy Shuck
    Date: 02/21/2021
    Class: CS350 Emerging Systems Architecture and Technology
    Term: 21EW3
    Assignment: 7-1 Final Project I

    This script will utilize a DHT sensor, light senor and three LEDs (red, green, blue) connected
    to a RaspberryPi.
    The temperature and humidity data will be collected via the DHT sensor but only during the
    daytime. Daytime will be defined by the light sensor and once it is dark data collection
    stops. Additionally, there are three LEDs that will light up to indicate specific situations.

    Green LED lights up when the last conditions are: temperature > 60 and < 85, and humidity is < 80%
    Blue LED lights up when the last conditions are: temperature > 85 and < 95, and humidity is < 80%
    Red LED lights up when the last conditions are: temperature > 95
    Green and Blue LED light up when the last conditions are: humidity > 80%
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


class LED:
    ON = 1
    OFF = 0


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


def TempToColor(temp):
    """
    Takes a temperature in Celsius and outputs an appropriate color
    :param temp: temperature to base the color from
    :return: RGB value of selected color
    """
    # color definitions are incremented every 2 degrees so that the index value is (degree / 2)
    color_defs = [
        (0, 0, 154),
        (0, 0, 180),
        (0, 0, 196),
        (0, 0, 208),
        (0, 0, 255),
        (5, 0, 255),
        (4, 0, 255),
        (3, 0, 255),
        (2, 0, 255),
        (1, 0, 255),
        (0, 0, 255),
        (0, 2, 255),
        (0, 18, 255),
        (0, 34, 255),
        (0, 50, 255),
        (0, 68, 255),
        (0, 84, 255),
        (0, 100, 255),
        (0, 116, 255),
        (0, 132, 255),
        (0, 148, 255),
        (0, 164, 255),
        (0, 180, 255),
        (0, 196, 255),
        (0, 212, 255),
        (0, 228, 255),
        (0, 255, 244),
        (0, 255, 208),
        (0, 255, 168),
        (0, 255, 131),
        (0, 255, 92),
        (0, 255, 54),
        (0, 255, 16),
        (23, 255, 0),
        (62, 255, 0),
        (101, 255, 0),
        (138, 255, 0),
        (176, 255, 0),
        (215, 255, 0),
        (253, 255, 0),
        (255, 250, 0),
        (255, 240, 0),
        (255, 230, 0),
        (255, 220, 0),
        (255, 210, 0),
        (255, 200, 0),
        (255, 190, 0),
        (255, 180, 0),
        (255, 170, 0),
        (255, 160, 0),
        (255, 150, 0),
        (255, 140, 0),
        (255, 130, 0),
        (255, 120, 0),
        (255, 110, 0),
        (255, 100, 0),
        (255, 90, 0),
        (255, 80, 0),
        (255, 70, 0),
        (255, 60, 0),
        (255, 50, 0),
        (255, 40, 0),
        (255, 30, 0),
        (255, 20, 0),
        (255, 10, 0),
        (255, 0, 0),
        (255, 0, 16),
        (255, 0, 32),
        (255, 0, 48),
        (255, 0, 64),
        (255, 0, 80),
        (255, 0, 96),
        (255, 0, 112),
        (255, 0, 128),
        (255, 0, 144),
        (255, 0, 160),
        (255, 0, 176),
        (255, 0, 192),
        (255, 0, 208),
        (255, 0, 224),
        (255, 0, 240),
        (255, 1, 240),
        (255, 2, 240),
        (255, 3, 240),
        (255, 4, 240),
        (255, 5, 240),
        (255, 6, 240),
        (255, 7, 240),
        (255, 8, 240),
        (255, 9, 240),
        (255, 10, 240),
        (255, 11, 240),
        (255, 12, 240),
        (255, 13, 240),
        (255, 14, 240),
        (255, 113, 245),
        (255, 129, 246),
        (255, 151, 248),
        (255, 179, 250),
        (255, 205, 251),
    ]

    # convert the celsius to fahrenheit, round up, then divide by 2 to identify teh array index
    index = int(math.ceil(CtoF(temp) / 2.0))
    # if index is greater than the number of degrees defined, then output the max color
    if index > len(color_defs):
        return color_defs[len(color_defs) - 1]
    # if index value is less than 0 then just return the coldest color at index 0
    if index < 0:
        return color_defs[0]

    # return the RGB color at index
    return color_defs[index]


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

    # LED port definitions for red, green, blue LEDs
    led_r = PORT.DIGITAL.D2  # red LED to D2
    led_g = PORT.DIGITAL.D4  # green LED to D4
    led_b = PORT.DIGITAL.D3  # blue LED to D3

    light_sensor = PORT.ANALOG.A1  # light sensor to A1
    K_threshold = 10  # Resistance threshold for detecting day vs night

    grovepi.pinMode(light_sensor, "INPUT")  # read sensor input
    grovepi.pinMode(led_r, "OUTPUT")  # red led light output
    grovepi.pinMode(led_g, "OUTPUT")  # green led light output
    grovepi.pinMode(led_b, "OUTPUT")  # blue led light output

    while True:
        try:
            if isDaylight(light_sensor, K_threshold):
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

                    # Program Specifications
                    # Green LED lights up when the last conditions are: temperature > 60 and < 85, and humidity is < 80%
                    # Blue LED lights up when the last conditions are: temperature > 85 and < 95, and humidity is < 80%
                    # Red LED lights up when the last conditions are: temperature > 95
                    # Green and Blue LED light up when the last conditions are: humidity > 80%
                    # FIXME: There is a potential bug in the logic here provided by the
                    #  customer specification. If humidity == 80% then no lights, If temp == 85%
                    #  or temp == 95% then potentially no lights. This is because the customer
                    #  did not state to have "less than or equal to" in their specification.

                    # start by turning off the LEDs
                    turn_off_leds([led_r, led_g, led_b])
                    if humidity > 80:
                        turn_on_leds([led_g, led_b])
                    elif temp > 95:
                        turn_on_leds([led_r])
                    elif 60 < temp < 85 and humidity < 80:
                        turn_on_leds([led_g])
                    elif 85 < temp < 95 and humidity < 80:
                        turn_on_leds([led_b])

            # Program specification states to only collect data every 30 minutes
            time.sleep(1800)  # run every 30 minutes

        except IOError as ioErr:
            turn_off_leds([led_r, led_g, led_b])
            errq.put_nowait(ioErr)
        except KeyboardInterrupt as kiErr:
            turn_off_leds([led_r, led_g, led_b])
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


def isDaylight(light_sensor, K_threshold):
    # read analog reading from sensor
    sensor_value = grovepi.analogRead(light_sensor)

    # Calculate specific resistance (K)
    K = float(1023 - sensor_value) * 10 / sensor_value

    if K > K_threshold:
        return True

    return False


def turn_on_leds(leds):
    """
    turn_on_leds is a helper function for processing the turning on of the LED lights.
    :param leds: array of led sensor locations
    :return: None
    """
    for led in leds:
        grovepi.digitalWrite(led, LED.ON)


def turn_off_leds(leds):
    """
        turn_off_leds is a helper function for processing the turning off of the LED lights.
        :param leds: array of led sensor locations
        :return: None
        """
    for led in leds:
        grovepi.digitalWrite(led, LED.OFF)


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
