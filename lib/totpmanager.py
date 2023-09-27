import totpgen
import adafruit_json_stream
import lib.computer_comms

class TOTPManager:
    keys = {}
    def __init__(self, comms:lib.computer_comms.ComputerComms, filepath=None):
        self.comms = comms
        self.filepath = filepath
        if self.filepath is not None:
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
    
    def add_key(self, service_name, secret, digits=6):
        if service_name in self.keys.keys():
            raise ValueError("Service already added!")
        self.keys[service_name] = {"secret": secret, "digits": digits}
    
    def remove_key(self, service_name):
        if service_name not in self.keys.keys():
            raise ValueError("Service does not exist")
        self.keys.pop(service_name)
    
    def gen_keys(self, time):
        result = {}
        for service_name in self.keys:
            service = self.keys[service_name]
            result[service_name] = totpgen.generate_otp(time // 30, service["secret"], service["digits"])
        return result
