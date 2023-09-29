import board
import digitalio
import analogio
import busio
import displayio
import adafruit_displayio_ssd1306
import lib.rv8803 as rv8803

class TOTKeyPins:
    def __init__(self):
        self.led1 = digitalio.DigitalInOut(board.GP25)
        self.led1.direction = digitalio.Direction.OUTPUT
        self.led2 = digitalio.DigitalInOut(board.GP20)
        self.led2.direction = digitalio.Direction.OUTPUT

        self.battery_sense = analogio.AnalogIn(board.GP27_A1)

        self.upButton = digitalio.DigitalInOut(board.GP18)
        self.upButton.direction = digitalio.Direction.INPUT
        self.upButton.pull = digitalio.Pull.UP
        self.centerButton = digitalio.DigitalInOut(board.GP10)
        self.centerButton.direction = digitalio.Direction.INPUT
        self.centerButton.pull = digitalio.Pull.UP
        self.downButton = digitalio.DigitalInOut(board.GP11)
        self.downButton.direction = digitalio.Direction.INPUT
        self.downButton.pull = digitalio.Pull.UP

        displayio.release_displays()
        i2c = busio.I2C(board.GP17, board.GP16)

        try:
            display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
            self.oled = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
        except ValueError:
            self.oled = None

        self.rtc = rv8803.RV8803(i2c)

    def get_voltage(self):
        return self.battery_sense.value * 3.3 / (4096*8)