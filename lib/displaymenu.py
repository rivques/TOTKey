from pins import InputEvent

class DisplayScreenBase:
    upper_level = None
    def display(self, splash):
        return self
    def take_input(self, event: InputEvent):
        if event.buttons == ["CENTER"] and event.isLongPress:
            # back button
            return self.upper_level
        elif event.buttons == ["UP","DOWN"] and event.isLongPress:
            # TODO: flip display
            pass
        return self

class ListMenu(DisplayScreenBase):
    def __init__(self, lower_levels):
        self.lower_levels = lower_levels
        self.selected_index = 0

    def display(self, splash):
        pass

    def take_input(self, event: InputEvent):
        if event.buttons == ["UP"] and not event.isLongPress:
            self.selected_index = max(0, self.selected_index - 1)
            return self
        elif event.buttons == ["DOWN"] and not event.isLongPress:
            self.selected_index = min(len(self.lower_levels) - 1, self.selected_index + 1)
            return self
        elif event.buttons == ["CENTER"] and not event.isLongPress:
            return self.lower_levels[self.selected_index]
        return super().take_input(event)
    

