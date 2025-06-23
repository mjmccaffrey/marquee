"""Marquee Lighted Sign Project - instruments"""

from abc import ABC, abstractmethod
import random
import time

from definitions import LIGHT_COUNT
from relays import RelayModuleInterface
from sequences import opposite

class Instrument(ABC):
    """"""
    accent_levels = 0
    pitch_levels = 0

    def __init__(self):
        super().__init__()

    @abstractmethod
    def play(self):
        """"""

class ActionInstrument(Instrument):
    """"""
    def __init__(self):
        super().__init__()

    def play(self):
        raise NotImplementedError

class RelayInstrument(Instrument):
    """"""
    def __init__(self, relays: RelayModuleInterface):
        super().__init__()
        self.relays = relays
        self.count = self.relays.relay_count
        self.relays.set_state_of_devices("0" * self.count)
        # time.sleep(2)
        self.pattern = self.relays.get_state_of_devices()
        assert self.pattern == "0" * self.count

    def select_relays(self, desired_state: str, desired_count: int) -> set[int]:
        candidates = [
            i
            for i, p in enumerate(self.pattern)
            if p == desired_state
        ]
        try:
            selected = set(random.sample(candidates, desired_count))
        except ValueError:
            #raise ValueError(
            print(
                f'{len(candidates)} of {desired_count} '
                f'{desired_state} relays present.'
            )
            selected = set(candidates)
        return selected

class BellSet(RelayInstrument):
    """"""
    pitch_levels = 9

    def __init__(self, relays: RelayModuleInterface):
        super().__init__(relays)

    def play(self, pitches: set[int]):
        """"""
        pattern = [
            '1' if i in pitches else '0'
            for i in range(self.pitch_levels)
        ]
        self.relays.set_state_of_devices(pattern)
        time.sleep(0.1)
        self.relays.set_state_of_devices(['0'] * self.pitch_levels)

class DrumSet(RelayInstrument):
    """"""
    accent_levels = 3
    accent_to_relay_count = {
        0: 2, 1: 4, 2: 8, 3: 16,
    }
    pitch_levels = 2
    pitch_to_relay_state = {
        0: '0', 1: '1',
    }

    def __init__(self, relays: RelayModuleInterface):
        super().__init__(relays)

    def play(self, accent: int, pitches: set[int]):
        """"""
        new_pattern = self.pattern
        desired_count = self.accent_to_relay_count[accent]
        for pitch in pitches:
            desired_state = self.pitch_to_relay_state[pitch]
            selected = self.select_relays(desired_state, desired_count)
            new_pattern = ''.join(
                opposite(p) if i in selected else p
                for i, p in enumerate(new_pattern)
            )
        self.relays.set_state_of_devices(new_pattern)
        print(self.pattern, new_pattern)
        self.pattern = new_pattern

class RestInstrument(Instrument):
    """"""
    def __init__(self):
        super().__init__()

    def play(self):
        raise NotImplementedError
