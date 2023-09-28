from pins import InputEvent
from adafruit_display_text import label, scrollable_label
import terminalio

class DisplayScreenBase:
    upper_level = None
    splash = None
    def update_display(self):
        pass
    def take_input(self, event: InputEvent):
        if event.buttons == set(["CENTER"]) and event.isLongPress:
            # back button
            return self.upper_level
        elif event.buttons == set(["UP","DOWN"]) and event.isLongPress:
            # TODO: flip display
            pass
        return None

class ListMenu(DisplayScreenBase):
    def __init__(self, lower_levels):
        self.lower_levels = lower_levels
        self.selected_index = 0
        self.old_selected_index = -1
        self.display_labels = [scrollable_label.ScrollingLabel(font=terminalio.FONT, text="", max_characters=21, y=(4+10*i)) for i in range(3)]
    
    def display_on(self, splash):
        for label in self.display_labels:
            splash.append(label)

    def update_display(self):
        if self.old_selected_index != self.selected_index:
            # display the 3 lines around the selected one
            levels_to_show = []
            shown_levels_start = 0
            if self.selected_index == 0:
                # we're at the top
                levels_to_show = self.lower_levels[:min(2, len(self.lower_levels)-1)]
                shown_levels_start = 0
            elif self.selected_index == len(self.lower_levels) - 1:
                # we're at the bottom
                levels_to_show = self.lower_levels[max(0, self.selected_index-2):]
                shown_levels_start = max(1, len(levels_to_show)-2)
            else:
                levels_to_show = self.lower_levels[self.selected_index-1:self.selected_index+1]
                shown_levels_start = self.selected_index - 1
            for i, label in enumerate(self.display_labels):
                label.text = levels_to_show[i]
                label.current_index = 0
                if self.selected_index - shown_levels_start == i:
                    label.color = 0x000000
                    label.background_color = 0xFFFFFF
                else:
                    label.color = 0xFFFFFF
                    label.background_color = 0x000000
            self.old_selected_index = self.selected_index
        
        for label in self.display_labels:
            label.update()

    def take_input(self, event: InputEvent):
        if event.buttons == set(["UP"]) and not event.isLongPress:
            self.selected_index = max(0, self.selected_index - 1)
            return None
        elif event.buttons == set(["DOWN"]) and not event.isLongPress:
            self.selected_index = min(len(self.lower_levels) - 1, self.selected_index + 1)
            return None
        elif event.buttons == set(["CENTER"]) and not event.isLongPress:
            return self.lower_levels[self.selected_index]
        return super().take_input(event)
    

