
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

# threshold denominator defines at what point the next LED should light up
threshold_denom = 35


while True:
    try:
        # Read the sound level
        sensor_value = grovepi.analogRead(snd_sensor)

        numLEDs = sensor_value / threshold_denom

        # IF no sound shut off the LEDs, if loud, illuminate LEDs
        if numLEDs < 1:
            grovepi.digitalWrite(led_low, LED_OFF)
            grovepi.digitalWrite(led_mid, LED_OFF)
            grovepi.digitalWrite(led_hi, LED_OFF)
        else:
            if 0 < numLEDs <= 1:
                # turn on led_low
                grovepi.digitalWrite(led_low, LED_ON)

                # turn off led_mid, led_hi
                grovepi.digitalWrite(led_mid, LED_OFF)
                grovepi.digitalWrite(led_hi, LED_OFF)

            elif 1 < numLEDs <= 2:
                # turn on led_low and led_mid
                grovepi.digitalWrite(led_low, LED_ON)
                grovepi.digitalWrite(led_mid, LED_ON)

                # turn off led_hi
                grovepi.digitalWrite(led_hi, LED_OFF)

            elif numLEDs > 3:
                # turn on led_low, led_mid, led_hi
                grovepi.digitalWrite(led_low, LED_ON)
                grovepi.digitalWrite(led_mid, LED_ON)
                grovepi.digitalWrite(led_hi, LED_ON)

        print("sensor_value = %d" %sensor_value)
        print("number of LEDs lit = %d" % numLEDs)

        time.sleep(.5)

    except IOError:
        print("Error")
