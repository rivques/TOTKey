import sys
import supervisor
import adafruit_json_stream
import asyncio

class ComputerComms:
    stdout = sys.stdout
    stdin = sys.stdin

    @property
    def serial_bytes_available(self):
        return supervisor.runtime.serial_bytes_available

    def __init__(self, pins):
        self.pins = pins

    def send_command(self, command, args):
        self.pins.led1.value=True
        print(adafruit_json_stream.json.dumps({"command": command, "args": args}))
        self.pins.led1.value=False

    def log(self, msg, level="INFO"):
        self.send_command("LOG", {"msg": msg, "level": level})

    async def get_command(self):
        theInput = await self.ainput("")
        try:
            return adafruit_json_stream.json.loads(theInput)
        except ValueError:
            print({"command": "INVALID_JSON", "args": {"input": theInput}})
            return None

    async def ainput(self, string: str) -> str:
        self.stdout.write(string)
        theInput = ""
        while "\n" not in theInput:
            await asyncio.sleep(0)
            # test for something on the line
            if(self.serial_bytes_available):
                theNewInput = self.stdin.read(1)
                # self.stdout.write(theNewInput) don't echo
                theInput += theNewInput
        return theInput
    