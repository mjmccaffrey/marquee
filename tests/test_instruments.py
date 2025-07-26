
from instruments import *
from relays import *

class RMI(RelayModuleInterface):
    relay_count = 8
    def get_state_of_devices(self):
        return "00000000"
    def set_state_of_devices(self, p):
        return None

class RI(RelayInstrument):
    def init(self, relays):
        super().__init__(relays)
    def play(self):
         pass

ri = RI(relays=RMI())

ri.pattern = "01010101"
assert ri.select_relays('0', 4) == {0, 2, 4, 6}
assert ri.select_relays('1', 4) == {1, 3, 5, 7}
