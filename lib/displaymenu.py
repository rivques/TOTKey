from pins import ButtonEvent

class DisplayScreenBase:
    upper_level = None
    def display(self, splash):
        return self
    def take_input(self, event: ButtonEvent):
        
        return self.upper_level

class ListMenu(DisplayScreenBase):
    def __init__(self, lower_levels):
        self.lower_levels = lower_levels
        self.selected_index = 0

    def display(self, splash)

