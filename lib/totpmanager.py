import totpgen
import adafruit_json_stream
import lib.computer_comms

class TOTPManager:
    keys = {}
    def __init__(self, comms:lib.computer_comms.ComputerComms, filepath=None):
        self.comms = comms
        self.filepath = filepath
        self.load_keys()
    
    def load_keys(self):
        filetext = ""
        with open(self.filepath) as f:
            filetext = "\n".join(f.readlines())
        self.keys = adafruit_json_stream.json.loads(filetext)
    
    def save_keys(self):
        try:
            with open(self.filepath, "w") as f:
                adafruit_json_stream.json.dump(self.keys, f)
        except OSError:
            self.comms.log("Filesystem not writeable!", "ERROR")
    
    def add_key(self, serviceName, secret, digits=6):
        if serviceName in self.keys.keys():
            raise ValueError("Service already added!")
        self.keys[serviceName] = {"secret": secret, "digits": digits}
    
    def remove_key(self, serviceName):
        if serviceName not in self.keys.keys():
            raise ValueError("Service does not exist")
        self.keys.pop(serviceName)
    
    def gen_keys(self, time):
        result = {}
        for serviceName in self.keys:
            service = self.keys[serviceName]
            result[serviceName] = totpgen.generate_otp(time // 30, service["secret"], service["digits"])
        return result
