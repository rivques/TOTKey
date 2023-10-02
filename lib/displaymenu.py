from inputclasses import InputEvent
from adafruit_display_text import label, scrolling_label
from adafruit_progressbar.horizontalprogressbar import HorizontalProgressBar
import terminalio
from pins import TOTKeyPins
import time
import storage

class DisplayScreenBase:
    upper_level = None
    splash = None
    comms = None
    def update_display(self):
        pass
    def take_input(self, event: InputEvent):
        if event.button == "CENTER" and event.isLongPress:
            # back button
            # self.comms.log("Back button pressed", "DEBUG")
            return self.upper_level
        return None

class ListMenu(DisplayScreenBase):
    def __init__(self, comms, lower_levels, upper_level=None):
        self.comms = comms
        self.lower_levels = lower_levels
        self.upper_level = upper_level
        self.selected_index = 0
        self.old_selected_index = -1
        self.display_labels = [scrolling_label.ScrollingLabel(font=terminalio.FONT, text=" ", max_characters=21, y=(4+10*i)) for i in range(3)]
        self.needs_update = True
    
    def display_on(self, splash):
        for label in self.display_labels:
            splash.append(label)
        self.needs_update = True

    def update_display(self, force_update=False):
        if self.old_selected_index != self.selected_index or force_update:
            # display the 3 lines around the selected one
            levels_to_show = []
            shown_levels_start = 0
            if self.selected_index == 0:
                # we're at the top
                levels_to_show = self.lower_levels[:min(3, len(self.lower_levels))]
                shown_levels_start = 0
            elif self.selected_index == len(self.lower_levels) - 1:
                # we're at the bottom
                levels_to_show = self.lower_levels[max(0, self.selected_index-2):]
                shown_levels_start = max(0, self.selected_index-2)
            else:
                levels_to_show = self.lower_levels[self.selected_index-1:self.selected_index+2]
                shown_levels_start = self.selected_index - 1
            for label in self.display_labels:
                label.text = " "
                label.color = 0xFFFFFF
                label.background_color = 0x000000
            for i in range(len(levels_to_show)):
                label = self.display_labels[i]
                label.text = levels_to_show[i]
                label.current_index = 0
                if self.selected_index - shown_levels_start == i:
                    label.color = 0x000000
                    label.background_color = 0xFFFFFF
                else:
                    label.color = 0xFFFFFF
                    label.background_color = 0x000000
            self.old_selected_index = self.selected_index
            self.needs_update = True
        
        for label in self.display_labels:
            if len(label.full_text) > label.max_characters or self.needs_update:
                label.update(force=self.needs_update)
        self.needs_update = False

    def take_input(self, event: InputEvent):
        if event.button == "UP" and not event.isLongPress:
            self.selected_index = max(0, self.selected_index - 1)
            # self.comms.log(f"Selected index: {self.selected_index}", "DEBUG")
            return None
        elif event.button == "DOWN" and not event.isLongPress:
            self.selected_index = min(len(self.lower_levels) - 1, self.selected_index + 1)
            # self.comms.log(f"Selected index: {self.selected_index}", "DEBUG")
            return None
        elif event.button == "CENTER" and not event.isLongPress:
            return self.lower_levels[self.selected_index]
        return super().take_input(event)
    

class KeyListMenu(ListMenu):
    def __init__(self, comms, totp_manager, upper_level=None):
        self.comms = comms
        self.totp_manager = totp_manager
        self.upper_level = upper_level
        self.selected_index = 0
        self.old_selected_index = -1
        self.display_labels = [scrolling_label.ScrollingLabel(font=terminalio.FONT, text=" ", max_characters=21, y=(4+10*i)) for i in range(3)]
        self.needs_update = True
    
    def display_on(self, splash):
        for label in self.display_labels:
            splash.append(label)
        self.needs_update = True
    
    def update_display(self):
        self.lower_levels = list(self.totp_manager.keys.keys())
        self.lower_levels.sort(key=lambda x: x.lower())
        if self.selected_index >= len(self.lower_levels):
            self.selected_index = len(self.lower_levels) - 1
        super().update_display(self.totp_manager.needs_display_update)
        self.totp_manager.needs_display_update = False
    
    def take_input(self, event: InputEvent):
        if event.button == "CENTER" and not event.isLongPress:
            self.totp_manager.select_key(self.lower_levels[self.selected_index])
            return "KeyShowMenu"
        else: return super().take_input(event)

class InfoMenu(DisplayScreenBase):
    def __init__(self, comms, pins: TOTKeyPins, upper_level):
        self.comms = comms
        self.pins = pins
        self.upper_level = upper_level
        fs_is_readonly = storage.getmount("/").readonly
        self.display_labels = [
            label.Label(terminalio.FONT, text=self.pins.rtc.get_datestring(), y=4),
            label.Label(terminalio.FONT, text=f"{self.pins.get_voltage():.3f} V", y=14),
            label.Label(terminalio.FONT, text=f"FS writeable to {'USB' if fs_is_readonly else 'CPy'}", y=24)
        ]
        self.last_update = time.monotonic()
    
    def display_on(self, splash):
        for label in self.display_labels:
            splash.append(label)
    
    def update_display(self):
        if time.monotonic() - self.last_update > 1:
            self.display_labels[0].text = self.pins.rtc.get_datestring()
            self.display_labels[1].text = f"{self.pins.get_voltage():.3f} V"
            self.last_update = time.monotonic()

class HelpMenu(DisplayScreenBase):
    def __init__(self, upper_level):
        self.upper_level = upper_level
        self.display_labels = [
            label.Label(terminalio.FONT, text="Welcome to TOTKey!", y=4),
            label.Label(terminalio.FONT, text="Use the down button", y=14),
            label.Label(terminalio.FONT, text="to advance this menu.", y=24),
        ]
        self.strings = [
            ["Welcome to TOTKey!", "Use the down button", "to advance this menu."],
            ["Use the up and down", "buttons to navigate", "through menus."],
            ["Click the center", "button to select an", "option."],
            ["Long-press the center", "button to go back", "to the previous menu."],
            ["Long-press the up or", "down buttons to", "rotate the display."],
            ["Manage keys by using", "the web interface", "on your computer."],
            ["To use a key,", "select the Keys menu", "then select a service."],
            ["You can either type", "the key in or press", "center to send it."],
            ["You can view info", "about the status", "by selecting Info."],
            ["If you plug in the", "board while holding", "the center button,"],
            ["the board will enter", "USB mode. You can", "then acess the FS."],
            ["See more at", "rivques/TOTKey", "on GitHub."]
        ]
        self.current_string = 0
        self.old_current_string = -1
    def display_on(self, splash):
        for label in self.display_labels:
            splash.append(label)
    
    def update_display(self):
        if self.current_string != self.old_current_string:
            for i in range(len(self.display_labels)):
                self.display_labels[i].text = self.strings[self.current_string][i]
            self.old_current_string = self.current_string
    
    def take_input(self, event: InputEvent):
        if event.button == "DOWN" and not event.isLongPress:
            self.current_string = min(len(self.strings) - 1, self.current_string + 1)
            return None
        elif event.button == "UP" and not event.isLongPress:
            self.current_string = max(0, self.current_string - 1)
            return None
        return super().take_input(event)

class KeyShowMenu(DisplayScreenBase):
    def __init__(self, comms, pins: TOTKeyPins, totp_manager, upper_level):
        self.comms = comms
        self.pins = pins
        self.totp_manager = totp_manager
        self.upper_level = upper_level
        self.key_label = label.Label(terminalio.FONT, text=" ", y=12, scale=2)
        self.service_name_label = scrolling_label.ScrollingLabel(terminalio.FONT, text=" ", y=26, max_characters=21, animate_time=0.3)
        self.progress_bar = HorizontalProgressBar((0, 0), (128, 1), max_value=30, bar_color=0xFFFFFF, fill_color=0x000000, border_thickness=0, margin_size=0)
        self.valid_until = 0
    
    def display_on(self, splash):
        self.valid_until = 0
        splash.append(self.key_label)
        splash.append(self.service_name_label)
        splash.append(self.progress_bar)
    
    def update_display(self):
        unixtime = self.pins.rtc.get_unixtime()
        time_spent = unixtime % 30
        self.progress_bar.value = time_spent
        if unixtime >= self.valid_until:
            self.valid_until = (unixtime // 30 + 1) * 30
            new_key = self.totp_manager.gen_key(unixtime)
            # self.comms.log(f"New key: {new_key}, Valid until: {self.valid_until}, Time now: {unixtime}", "DEBUG")
            self.key_label.text = new_key
            self.service_name_label.text = self.totp_manager.selected_key
            self.service_name_label.update()
            return
        
        if self.service_name_label.max_characters < len(self.totp_manager.selected_key):
            self.service_name_label.update()


    def take_input(self, event: InputEvent):
        if event.button == "CENTER" and not event.isLongPress:
            self.comms.send_keys(self.key_label.text)
            return self.upper_level
        else: return super().take_input(event)
            
def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min