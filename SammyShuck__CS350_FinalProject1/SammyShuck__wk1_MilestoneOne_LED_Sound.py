"""
    SammyShuck__wk1_MilestoneOne_LED_Sound.py

    Name: Sammy Shuck
    Date: 01/17/2021
    Class: CS350 Emerging Systems Architecture and Technology
    Term: 21EW3
    Assignment: 2-3 Final Project Milestone One: Adding and LED and Sound

    This script will utilize a sound sensor and three LEDs connected to a RaspberryPi.
    Depending on the sound threshold will indicate which of the three LED lights will
    illuminate. This is similar to that of an audio VU Meter.
"""

import grovepi
import time
import enum


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


# Port Definitions for LED
led_low = PORT.DIGITAL.D2
led_mid = PORT.DIGITAL.D3
led_hi = PORT.DIGITAL.D4
# LED ON/OFF values
LED_ON = 1
LED_OFF = 0

# sound sensor port definition A2
snd_sensor = PORT.ANALOG.A2

# configure the pinMode input to sound sensor
grovepi.pinMode(snd_sensor, "INPUT")
# configure the pinMode output to use all three LEDs
grovepi.pinMode(led_low, "OUTPUT")
grovepi.pinMode(led_mid, "OUTPUT")
grovepi.pinMode(led_hi, "OUTPUT")

# threshold to turn the led_low on 125.00 * 5 / 1024 = 0.61v
low_thres = 200
# threshold to turn the led_mid on 400.00 * 5 / 1024 = 1.95v
mid_thres = 500
# threshold to turn the led_hi on 700.00 * 5 / 1024 = 3.41v
hi_thres = 650


def delay(t=0.0):
    time.sleep(t)


def blink_leds(leds):
    for led in leds:
        grovepi.digitalWrite(led, LED_ON)
        delay()

    for led in leds:
        grovepi.digitalWrite(led, LED_OFF)


while True:
    try:
        # Read the sound level
        sensor_value = grovepi.analogRead(snd_sensor)

        #print("sensor_value = %d" % sensor_value)

        # IF no sound shut off the LEDs, if loud, illuminate LEDs
        if sensor_value <= low_thres:
            #print("all leds off")
            grovepi.digitalWrite(led_low, LED_OFF)
            grovepi.digitalWrite(led_mid, LED_OFF)
            grovepi.digitalWrite(led_hi, LED_OFF)
            delay()

        else:
            if low_thres <= sensor_value < mid_thres:

                # turn off led_mid, led_hi
                grovepi.digitalWrite(led_mid, LED_OFF)
                grovepi.digitalWrite(led_hi, LED_OFF)

                # turn on led_low
                print("led_low = on")
                blink_leds([led_low])

            elif mid_thres <= sensor_value < hi_thres:
                # turn off led_hi
                grovepi.digitalWrite(led_hi, LED_OFF)

                # turn on led_low
                print("led_low, led_mid = on")
                blink_leds([led_low, led_mid])

            elif sensor_value >= hi_thres :
                # turn on led_low, led_mid, led_hi
                print("led_low, led_mid, led_hi = on")
                blink_leds([led_low, led_mid, led_hi])

    except IOError:
        print("Error")
