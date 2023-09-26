from lib.pins import TOTKeyPins
import asyncio
from lib.computer_comms import ComputerComms

class TOTKey:
    def __init__(self, pins, comms):
        self.pins: TOTKeyPins = pins
        self.comms: ComputerComms = comms
        self.running = True
        self.input_events = []
        asyncio.run(self.do_tasks())

    async def do_tasks(self):
        self.comms.log("TOTKey starting up...")
        self.input_task = asyncio.create_task(self.process_inputs())
        self.usb_task = asyncio.create_task(self.handle_computer())
        self.display_task = asyncio.create_task(self.run_display())
        await self.wait_for_finish()
        self.comms.log("All tasks finished. Thanks for using TOTKey.")
        
    async def wait_for_finish(self):
        asyncio.gather(self.input_task, self.usb_task, self.display_task)

    async def process_inputs(self):
        while self.running:
            asyncio.sleep(0)
    
    async def handle_computer(self):
        while self.running:
            asyncio.sleep(0)
    
    async def run_display(self):
        while self.running:
            asyncio.sleep(0)
    
totKey = TOTKey(TOTKeyPins()) # start and run TOTKey firmware