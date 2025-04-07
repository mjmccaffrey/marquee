
from abc import ABC, abstractmethod
from typing import Any, Callable

class Instrument(ABC):
    """"""
    allows_pitches = False
    allows_accents = False
    allows_actions = False

    def __init__(
        self, 
    ):
        super().__init__()

    @abstractmethod
    def play(self):
        """"""

class ActionInstrument(Instrument):
    """"""
    allows_pitches = False
    allows_accents = False
    allows_actions = True

    def __init__(
        self, 
    ):
        super().__init__()

    def play(self):
        """"""

class BellSet(Instrument):
    """"""
    allows_pitches = True
    allows_accents = False
    allows_actions = False

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
    allows_pitches = False
    allows_accents = True
    allows_actions = False

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
    allows_pitches = False
    allows_accents = False
    allows_actions = False

    def __init__(
        self, 
    ):
        super().__init__()

    def play(self):
        """"""
