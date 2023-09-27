from adafruit_bus_device import i2c_device
from adafruit_register import i2c_bcd_datetime
from busio import I2C
import adafruit_datetime
import time

class RV8803:
    date = i2c_bcd_datetime.BCDDateTimeRegister(0x00, weekday_first=True, weekday_start=0)
    
    def __init__(self, i2c: I2C, device_address=0x32):
        self.i2c = i2c
        self.device_address = device_address
        self.i2c.try_lock() # wake up the RTC / get it to respond
        self.i2c.scan() # no idea why this is needed, probably a side effect of scan()
        self.i2c.unlock()

        self.i2c_device = i2c_device.I2CDevice(self.i2c, self.device_address)
    
    def get_unixtime(self):
        date = self.date
        return time.mktime(date)
    
    def set_datetime(self, date: adafruit_datetime.datetime):
        # IN UTC!! (no timezone or DST support)
        self.date = time.struct_time([date.year, date.month, date.day, date.hour, date.minute, date.second, date.weekday(), -1, -1])
        

if __name__ == "__main__":
    # TODO: test the RV8803
    import pins
    rtc = RV8803(pins.TOTKeyPins().i2c)
    print("rtc created")
    print(rtc.date)
    print(rtc.get_datetime())
    rtc.set_datetime(adafruit_datetime.datetime(2023, 9, 27, 12, 22, 14))
    print(rtc.date)
    print(rtc.get_datetime())