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
        else:
            self.keys = {
                "No file": {"secret": "2test", "digits": 6},
                "A really long service name": {"secret": "test3", "digits": 6}
            }
        self.needs_display_update = True
        self.selected_key = None
    
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
        # make sure secret is valid
        totpgen.generate_otp(0, secret, digits)
        self.keys[service_name] = {"secret": secret, "digits": digits}
        self.save_keys()
        self.needs_display_update = True
    
    def remove_key(self, service_name):
        if service_name not in self.keys.keys():
            raise ValueError("Service does not exist")
        self.keys.pop(service_name)
        self.save_keys()
        self.needs_display_update = True
    
    def gen_key(self, time):
        if self.selected_key is None:
            raise ValueError("No key selected")
        return totpgen.generate_otp(time // 30, self.keys[self.selected_key]["secret"], self.keys[self.selected_key]["digits"])
    
    def select_key(self, service_name):
        if service_name not in self.keys.keys():
            raise ValueError("Service does not exist")
        self.selected_key = service_name
