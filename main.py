from lib.pins import TOTKeyPins
import asyncio
from lib.computer_comms import ComputerComms
import time
import adafruit_datetime

class InputEvent:
    def __init__(self, button, action):
        self.button = button
        self.action = action
        self.time = time.monotonic()

class TOTKey:
    def __init__(self, pins, comms):
        self.pins: TOTKeyPins = pins
        self.comms: ComputerComms = comms
        self.running = True
        self.input_events = []
        self.button_states = [True, True, True]
        self.comp_commands = []

        asyncio.run(self.do_tasks())

    async def do_tasks(self):
        self.comms.log("TOTKey starting up...")
        self.input_task = asyncio.create_task(self.process_inputs())
        self.usb_task = asyncio.create_task(self.handle_computer())
        self.display_task = asyncio.create_task(self.run_display())
        await self.wait_for_finish()
        self.comms.log("All tasks finished. Thanks for using TOTKey.")
        
    async def wait_for_finish(self):
        await asyncio.gather(self.input_task, self.usb_task, self.display_task)

    async def process_inputs(self):
        while self.running:
            if self.button_states[0] != self.pins.upButton.value:
                self.button_states[0] = self.pins.upButton.value
                self.input_events.append(InputEvent("UP", "PRESSED" if not self.button_states[0] else "RELEASED"))
            if self.button_states[1] != self.pins.centerButton.value:
                self.button_states[1] = self.pins.centerButton.value
                self.input_events.append(InputEvent("CENTER", "PRESSED" if not self.button_states[1] else "RELEASED"))
            if self.button_states[2] != self.pins.downButton.value:
                self.button_states[2] = self.pins.downButton.value
                self.input_events.append(InputEvent("DOWN", "PRESSED" if not self.button_states[2] else "RELEASED"))
            await asyncio.sleep(0)
    
    async def handle_computer(self):
        self.computer_input_task = asyncio.create_task(self.handle_computer_input())
        self.computer_output_task = asyncio.create_task(self.handle_computer_output())
        while self.running:
            await asyncio.sleep(0)
        self.computer_input_task.cancel() # don't get stuck in ainput()
        await asyncio.gather(self.computer_output_task)

    async def handle_computer_input(self):
        while self.running:
            command = await self.comms.get_command()
            if command is not None:
                self.comp_commands.append(command)
    
    async def handle_computer_output(self):
        self.comms.send_command("BOARD_READY", {})
        while self.running:
            if len(self.comp_commands) > 0:
                command = self.comp_commands.pop(0)
                await self.handle_command(command)
            
            await asyncio.sleep(0)
    
    async def handle_command(self, command):
        if command["command"] == "INIT_COMMS":
            self.comms.send_command("COMMS_START_ACK", {"current_time": self.pins.rtc.get_datetime()._mktime()})
        elif command["command"] == "SET_TIME":
            self.pins.rtc.set_datetime(adafruit_datetime.datetime.fromtimestamp(command["args"]["current_time"]))
            self.comms.send_command("TIME_SET_ACK", {"current_time": self.pins.rtc.get_datetime()._mktime()})
        elif command["command"] == "GET_TIME":
            self.comms.send_command("TIME_GET_RES", {"current_time": self.pins.rtc.get_datetime()._mktime()})
        elif command["command"] == "BLINK_LED":
            self.comms.send_command("BLINK_ACK", {})
            self.pins.led2.value = not self.pins.led2.value
            await asyncio.sleep(0.5)
            self.pins.led2.value = not self.pins.led2.value
        elif command["command"] == "HALT":
            self.comms.send_command("HALT_ACK", {})
            self.running = False
        else:
            self.comms.log(f"Unknown command: {command}", "WARNING")

    async def run_display(self):
        while self.running:
            if len(self.input_events) > 0:
                event = self.input_events.pop(0)
                self.comms.log(f"Input event: {event.button} {event.action}", "DEBUG")
            await asyncio.sleep(0)

    
print("starting...")
pins = TOTKeyPins()
totKey = TOTKey(pins, ComputerComms(pins)) # start and run TOTKey firmware