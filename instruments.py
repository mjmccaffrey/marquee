"""Marquee Lighted Sign Project - instruments"""

from abc import ABC, abstractmethod

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
    ):
        super().__init__()
        accent_to_relay_count = {
        '-': 4, '>': 8, '^': 12,
        }

    def play(self):
        """"""

class RestInstrument(Instrument):
    """"""
    def __init__(
        self, 
    ):
        super().__init__()

    def play(self):
        """"""
