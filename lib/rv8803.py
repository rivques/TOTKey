import adafruit_bus_device

class RV8803:
    def __init__(self, i2c, device_address=0b0110010):
        self.i2c = i2c
        self.device_address = device_address