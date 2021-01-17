"""
    SammyShuck__wk2_MilestoneOne_LED_Sound.py

    Name: Sammy Shuck
    Date: 01/17/2021
    Class: CS350 Emerging Systems Architecture and Technology
    Term: 21EW3
    Assignment: 2-3 Final Project Milestone One: Adding an LED and Sound

    This script will utilize a sound sensor and three LEDs connected to a RaspberryPi.
    Depending on the sound threshold will indicate which of the three LED lights will
    illuminate. This is similar to that of an audio VU Meter.
"""

# Import statements
import grovepi
import math
import time
import sys

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


class LCD:
    # LCD constants
    # this device has two I2C addresses
    DISPLAY_RGB_ADDR = 0x62
    DISPLAY_TEXT_ADDR = 0x3e

    # class constructor with optional RGB values
    def __init__(self, r=0, g=0, b=0):
        """
        Class constructor for teh LCD screen handling
        :param r: Red color value
        :param g: Green color value
        :param b: Blue color value
        """
        self.__r = r
        self.__g = g
        self.__b = b
        self.__text = ""

    @staticmethod
    def _delay(t=0.5):
        """
        private method for pausing the program for `t` seconds
        :param t: float value in seconds to delay
        """
        time.sleep(t)

    def _return_cursor_home(self):
        """
        Returns the cursor to the home position 0x02
        """
        self.sendCommand(0x02)
        self._delay()

    def _prep_screen(self, no_refresh=False):
        """
        Prepares the screen for beign written to
        """

        self._return_cursor_home()
        if not no_refresh:
            self.clearScreen()
        self.sendCommand(0x08 | 0x04)  # display on, no cursor
        self.sendCommand(0x28)  # two lines
        self._delay()  # delay the default amount of time

    def _send_text(self):
        """
        Sends the text to the writer checking for new line characters and End of Line
        situations
        :return:
        """
        row = 0  # max 2 rows
        chr_count = 0  # max 16 characters

        for c in self.__text:
            # LCD is capable of 2 rows of 16 Characters
            if c == '\n' or chr_count == 16:
                chr_count = 0
                row += 1
                if row == 2:
                    break
                self.sendCommand(0xc0)
                if c == '\n':
                    continue
            chr_count += 1
            self._write(0x40, ord(c))

    def _write(self, *args):
        """
        Writes the data to the bus
        :param args: array of values for writing
        """
        bus.write_byte_data(self.DISPLAY_TEXT_ADDR, *args)

    def _write_rgb(self):
        bus.write_byte_data(self.DISPLAY_RGB_ADDR, 0, 0)
        bus.write_byte_data(self.DISPLAY_RGB_ADDR, 1, 0)
        bus.write_byte_data(self.DISPLAY_RGB_ADDR, 0x08, 0xaa)
        bus.write_byte_data(self.DISPLAY_RGB_ADDR, 4, self.__r)
        bus.write_byte_data(self.DISPLAY_RGB_ADDR, 3, self.__g)
        bus.write_byte_data(self.DISPLAY_RGB_ADDR, 2, self.__b)

    def setRGB(self, r, g, b):
        """
        setter for the R, G, B properties
        :param r: Red color value
        :param g: Green color value
        :param b: Blue color value
        """
        self.__r = r
        self.__g = g
        self.__b = b

        self._write_rgb()

    def clearScreen(self):
        """
        Clears the LCD screen of any contents
        """
        self.sendCommand(0x01)
        self._delay()  # delay the default amount of time

    def sendCommand(self, cmd):
        """
        Sends the command `cmd` to the LCD display
        :param cmd: byte value
        """
        self._write(0x80, cmd)

    def prints(self, text):
        """
        Sets the LCD screen text. Use \n to move to the second line.
        Otherwise, the line will auto-wrap
        :param text: string data to display onto the LCD screen
        """
        self.__text = text
        self._prep_screen()
        self._send_text()

    def prints_no_refresh(self, text):
        """
        Same as print but updates teh LCD screen without clearing the display first
        :param text: string data to display onto the LCD screen
        """
        self.__text = text
        self._prep_screen(no_refresh=True)
        self._send_text()

    def create_custom_char(self, location, pattern):
        """
        Using an array of row patterns, create a custom character or image.
        Writes a bit pattern to LCD CGRAM
        :param location: integer, one of 8 slots (0-7)
        :param pattern: byte array containing the bit pattern, like as found at
               https://omerk.github.io/lcdchargen/
        """
        location &= 0x07  # Make sure the location is 0-7
        self.sendCommand(0x40 | (location << 3))
        self._write(0x40, pattern)


class DHT:
    BLUE = 0
    WHITE = 1


def CtoF(C):
    """
    Converts Celcius to Fahrenheit
    :param C: float valu in degrees Celsius
    :return: float value in degrees Fahrenheit
    """
    return float(C * (9/5) + 32)


def TempToColor(temp):
    """
    Takes a temperature in Celsius and outputs an appropriate color
    :param temp:
    :return:
    """
    color_defs = [
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
        (255, 224, 255),
    ]

    if temp > len(color_defs):
        return color_defs[len(color_defs) - 1]
    if temp < 0:
        return color_defs[0]

    return color_defs[math.ceil(temp)]


def main():
    """
    main function declaration for main program execution
    :return:
    """
    lcd = LCD()
    lcd.setRGB(0, 128, 64)
    lcd.clearScreen()
    dht_sensor_port = PORT.DIGITAL.D4
    dht_sensor_type = DHT.BLUE

    while True:
        try:
            [temp, humidity] = grovepi.dht(dht_sensor_port, dht_sensor_type)
            if math.isnan(temp) is False and math.isnan(humidity) is False:
                txt = ("Temp: %.02fC\nHumidity: %.02f%%" % (temp, humidity))
                print(txt)
                lcd.setRGB(*TempToColor(temp))
                lcd.prints_no_refresh(txt)

        except (IOError, TypeError) as e:
            print("Error occurred: " + str(e))
            break
        except KeyboardInterrupt as e:
            print("Keyboard Interrupt error: " + str(e))
            lcd.clearScreen()
            break


if __name__ == "__main__":
    main()
