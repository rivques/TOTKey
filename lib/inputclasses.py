import time

class InputEvent:
    def __init__(self, button, isLongPress):
        self.button = button
        self.isLongPress = isLongPress

class ButtonPress:
    def __init__(self, button):
        self.button = button
        self.time = time.monotonic()