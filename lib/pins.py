import board
import digitalio
import analogio
import busio
import displayio
import adafruit_displayio_ssd1306
import lib.rv8803 as rv8803

class ButtonEvent:
    def __init__(self, button, action):
        self.button = button
        self.action = action
        self.time = time.monotonic()

class TOTKeyPins:
    led1 = digitalio.DigitalInOut(board.GP25)
    led1.direction = digitalio.Direction.OUTPUT
    led2 = digitalio.DigitalInOut(board.GP20)
    led2.direction = digitalio.Direction.OUTPUT

    battery_sense = analogio.AnalogIn(board.GP27_A1)

    upButton = digitalio.DigitalInOut(board.GP18)
    upButton.direction = digitalio.Direction.INPUT
    upButton.pull = digitalio.Pull.UP
    centerButton = digitalio.DigitalInOut(board.GP10)
    centerButton.direction = digitalio.Direction.INPUT
    centerButton.pull = digitalio.Pull.UP
    downButton = digitalio.DigitalInOut(board.GP11)
    downButton.direction = digitalio.Direction.INPUT
    downButton.pull = digitalio.Pull.UP

    displayio.release_displays()
    i2c = busio.I2C(board.GP17, board.GP16)

    display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
    oled = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

    rtc = rv8803.RV8803(i2c)

    def get_voltage(self):
        return self.battery_sense.value * 3.3 / (4096*8)