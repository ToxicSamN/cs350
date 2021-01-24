"""
    SammyShuck__wk4_MilestoneThree_LightSense_LED.py

    Name: Sammy Shuck
    Date: 01/31/2021
    Class: CS350 Emerging Systems Architecture and Technology
    Term: 21EW3
    Assignment: 4-3 Final Project Milestone Three: Interrupts Detecting Light Conditions

    This script will utilize a light sensor and a LED connected to a RaspberryPi.
    The LED will light ON if current readings for light sensor reach a defined threshold and turn
    off when threshold is not met.
"""

# Import statements
import grovepi
import time


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


if __name__ == "__main__":
    try:
        led_status = LED.OFF

        # Setting the light sensor to Analog 0 port
        light_sensor = PORT.ANALOG.A0
        # setting the LED light to digital 4 port
        led = PORT.DIGITAL.D4

        # threshold for turning on and off the LED light
        light_threshold = 10

        grovepi.pinMode(light_sensor, "INPUT")  # read sensor input
        grovepi.pinMode(led, "OUTPUT")  # led light output

        while True:
            # read analog reading from sensor
            sensor_value = grovepi.analogRead(light_sensor)

            # Calculate specific resistance (K)
            K = float(1023 - sensor_value) * 10 / sensor_value

            if K > light_threshold and led_status == LED.OFF:
                # turn on LED
                print("LED ON")
                grovepi.digitalWrite(led, LED.ON)
            elif K <= light_threshold and led_status == LED.ON:
                # turn off LED
                print("LED OFF")
                grovepi.digitalWrite(led, LED.OFF)
            else:
                print("unhandled condition .. what did you do?")
                raise BaseException("Ya done messed up A-A-Ron")

    except BaseException as e:
        print("\nException: Cleaning up")
        # turn off LED
        grovepi.digitalWrite(led, LED.OFF)
        raise e
