import lib.pins
import displayio
from adafruit_display_text import label, scrolling_label
import terminalio
import time

pins = lib.pins.TOTKeyPins()
# can we fit 3 lines of text on the screen?
splash = displayio.Group()
pins.oled.show(splash)
# splash.append(label.Label(terminalio.FONT, text="TOTKey booting up...", y=4))
# splash.append(label.Label(terminalio.FONT, text="2O2Key booting up...", y=14))
# splash.append(label.Label(terminalio.FONT, text="3O3Key booting up...", y=24))
# splash.append(label.Label(terminalio.FONT, text="4O4Key booting up...", y=34))
# time.sleep(10)
# while len(splash) > 0:
#     splash.pop()
splash.append(label.Label(terminalio.FONT, text="123456", scale=2,y=12))
my_scr_label = scrolling_label.ScrollingLabel(terminalio.FONT, text="Option A: A very long string that needs to scroll",y=26,max_characters=21, animate_time=0.3)
splash.append(my_scr_label)
while True:
    my_scr_label.update()