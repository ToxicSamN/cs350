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

# LED port definitions 2=D2, 3=D3, 4=D4
led_low = 2
led_mid = 3
led_hi = 4
# LED ON/OFF values
LED_ON = 1
LED_OFF = 0

# sound sensor port definition.
# sound sensor is an analog sensor, valid options are 0=A0, 1=A1, 2=A2
snd_sensor = 0

# configure the pinMode input to sound sensor
grovepi.pinMode(snd_sensor, "INPUT")
# configure the pinMode output to use all three LEDs
grovepi.pinMode(led_low, "OUTPUT")
grovepi.pinMode(led_mid, "OUTPUT")
grovepi.pinMode(led_hi, "OUTPUT")

# threshold to turn the led_low on 125.00 * 5 / 1024 = 0.61v
low_thres = 125
# threshold to turn the led_mid on 400.00 * 5 / 1024 = 1.95v
mid_thres = 250
# threshold to turn the led_hi on 700.00 * 5 / 1024 = 3.41v
hi_thres = 375


def delay(t=0.5):
    time.sleep(t)


def blink_leds(leds):
    for l in leds:
        grovepi.digitalWrite(l, LED_ON)
        delay()

    for l in leds:
        grovepi.digitalWrite(l, LED_OFF)


while True:
    try:
        # Read the sound level
        sensor_value = grovepi.analogRead(snd_sensor)

        print("sensor_value = %d" % sensor_value)

        # IF no sound shut off the LEDs, if loud, illuminate LEDs
        if sensor_value <= low_thres:
            print("all leds off")
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
