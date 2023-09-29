from lib.pins import TOTKeyPins
from lib.inputclasses import InputEvent, ButtonPress
import asyncio
from lib.computer_comms import ComputerComms
import time
import adafruit_datetime
import lib.totpmanager
import displayio
from adafruit_display_text import label
import terminalio
import lib.displaymenu
import storage

class TOTKey:
    LONG_THRESHOLD = 0.5
    def __init__(self, pins, comms):
        self.pins: TOTKeyPins = pins
        self.comms: ComputerComms = comms
        self.running = True
        self.button_presses = []
        self.button_states = [True, True, True]
        self.inputs = []
        self.comp_commands = []
        self.current_menu = None
        filepath = "/keys.json"
        self.totp_manager = lib.totpmanager.TOTPManager(comms, filepath if not storage.getmount("/").readonly else None)
        self.menus = { # key: menu name, value: DisplayScreenBase descendent
            "Main": lib.displaymenu.ListMenu(comms, ["Keys", "Info", "Settings"]),
            "Info": lib.displaymenu.InfoMenu(comms, pins, "Main"),
            "Keys": lib.displaymenu.KeyListMenu(comms, self.totp_manager, "Main"),
            "KeyShowMenu": lib.displaymenu.KeyShowMenu(comms, pins, self.totp_manager, "Keys")
        }

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
    
    def input_from_button_press(self, button):
        for event in self.button_presses:
            if event.button == button:
                self.inputs.append(InputEvent(button, time.monotonic() - event.time > self.LONG_THRESHOLD))
                self.button_presses.remove(event)
                break

    async def process_inputs(self):
        while self.running:
            if self.button_states[0] != self.pins.upButton.value:
                self.button_states[0] = self.pins.upButton.value
                if not self.button_states[0]:
                    self.button_presses.append(ButtonPress("UP"))
                else:
                    self.input_from_button_press("UP")
                    
            if self.button_states[1] != self.pins.centerButton.value:
                self.button_states[1] = self.pins.centerButton.value
                if not self.button_states[1]:
                    self.button_presses.append(ButtonPress("CENTER"))
                else:
                    self.input_from_button_press("CENTER")
            if self.button_states[2] != self.pins.downButton.value:
                self.button_states[2] = self.pins.downButton.value
                if not self.button_states[2]:
                    self.button_presses.append(ButtonPress("DOWN"))
                else:
                    self.input_from_button_press("DOWN")
            for button_press in self.button_presses:
                if time.monotonic() - button_press.time > self.LONG_THRESHOLD:
                    self.inputs.append(InputEvent(button_press.button, True))
                    self.button_presses.remove(button_press)         
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
            self.comms.send_command("COMMS_START_ACK", {"current_time": self.pins.rtc.get_unixtime()})
        elif command["command"] == "SET_TIME":
            self.pins.rtc.set_datetime(adafruit_datetime.datetime.fromtimestamp(command["args"]["current_time"]))
            self.comms.send_command("TIME_SET_ACK", {"current_time": self.pins.rtc.get_unixtime()})
        elif command["command"] == "GET_TIME":
            self.comms.send_command("TIME_GET_RES", {"current_time": self.pins.rtc.get_unixtime()})
        elif command["command"] == "BLINK_LED":
            self.comms.send_command("BLINK_ACK", {})
            self.pins.led2.value = not self.pins.led2.value
            await asyncio.sleep(0.5)
            self.pins.led2.value = not self.pins.led2.value
        elif command["command"] == "ADD_KEY":
            try:
                self.totp_manager.add_key(command["args"]["service_name"], command["args"]["secret"], command["args"]["digits"])
                self.comms.send_command("KEY_ADD_ACK", {})
            except ValueError as e:
                self.comms.log(f"Error adding key: {e}", "ERROR")
        elif command["command"] == "REMOVE_KEY":
            try:
                self.totp_manager.remove_key(command["args"]["service_name"])
                self.comms.send_command("KEY_REMOVE_ACK", {})
            except ValueError as e:
                self.comms.log(f"Error removing key: {e}", "ERROR")
        elif command["command"] == "LIST_KEYS":
            self.comms.send_command("KEY_LIST_RESPONSE", {"keys": list(self.totp_manager.keys.keys())})
        elif command["command"] == "GET_VOLTAGE":
            self.comms.send_command("VOLTAGE_GET_RESPONSE", {"voltage": str(self.pins.get_voltage())})
        elif command["command"] == "HALT":
            self.running = False
        else:
            self.comms.log(f"Unknown command: {command['command']}", "WARNING")

    async def run_display(self):
        if self.pins.oled is None:
            return
        self.splash = displayio.Group()
        current_time = pins.rtc.get_datestring()
        self.splash.append(label.Label(terminalio.FONT, text=f"TOTKey booting up...\n{current_time}", y=4))
        self.pins.oled.show(self.splash)
        await asyncio.sleep(1)
        self.splash = displayio.Group()
        self.current_menu = self.menus["Main"]
        self.current_menu.display_on(self.splash)
        self.pins.oled.show(self.splash)
        while self.running:
            self.current_menu.update_display()
            if len(self.inputs) > 0:
                event = self.inputs.pop(0)
                if event.button == "UP" and event.isLongPress:
                    self.pins.oled.rotation = 0
                elif event.button == "DOWN" and event.isLongPress:
                    self.pins.oled.rotation = 180
                else:
                    if self.pins.oled.rotation == 180:
                        if event.button == "UP":
                            event.button = "DOWN"
                        elif event.button == "DOWN":
                            event.button = "UP"
                    new_menu = self.current_menu.take_input(event)
                    if new_menu is not None:
                        self.current_menu = self.menus[new_menu]
                        while len(self.splash) > 0:
                            self.splash.pop()
                        self.current_menu.display_on(self.splash)
                        self.pins.oled.show(self.splash)
            await asyncio.sleep(0)

pins = TOTKeyPins()
totKey = TOTKey(pins, ComputerComms(pins)) # start and run TOTKey firmware