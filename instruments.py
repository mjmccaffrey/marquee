"""Marquee Lighted Sign Project - instruments"""

from abc import ABC, abstractmethod
from relays import NumatoUSBRelayModule

class Instrument(ABC):
    """"""
    def __init__(
        self, 
    ):
        super().__init__()

    @abstractmethod
    def play(self):
        """"""

class ActionInstrument(Instrument):
    """"""
    def __init__(
        self, 
    ):
        super().__init__()

    def play(self):
        """"""

class BellSet(Instrument):
    """"""
    def __init__(
        self, 
    ):
        super().__init__()
        #pitch_to_relay: dict[str, int] = {
        #    p: l for l, p in enumerate(pitches)
        #}

    def play(self):
        """"""

class DrumSet(Instrument):
    """"""
    def __init__(
        self,
        relays: NumatoUSBRelayModule,
    ):
        super().__init__()
        self.relays = relays
        self.count = self.relays.relay_count
        self.relays.set_state_of_devices("0" * self.count)
        self.pattern = self.relays.get_state_of_devices()
        assert self.pattern == "0" * self.count
        self.click_next = 0

    def play(self, accent: str):
        """"""
        accent_to_relay_count = {
            '': 2, '-': 4, '>': 8, '^': 12,
        }
        pattern = self.pattern
        for r in range(accent_to_relay_count[accent]):
            i = (self.click_next + r) % self.count
            pattern = (
                  pattern[ : i ]
                + '0' if pattern[i] == '1' else '1'
                + pattern[ i + 1 : ]
            )
            print(i, pattern)
            self.click_next = i + (1 % self.count)
            self.relays.set_state_of_devices(pattern)
            self.pattern = pattern

class RestInstrument(Instrument):
    """"""
    def __init__(
        self, 
    ):
        super().__init__()

    def play(self):
        """"""
