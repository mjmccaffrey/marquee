"""Marquee Lighted Sign Project - instruments"""

from abc import ABC, abstractmethod
from collections.abc import Collection
import random

from configuration import LIGHT_COUNT
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
            print(
                f'{len(candidates)} of {desired_count} '
                f'{desired_state} relays present.'
            )
            selected = set(candidates)
        return selected

class BellSet(RelayInstrument):
    """"""
    strike_time = 0.1
    pitch_levels = 8

    def __init__(self, relays: RelayModuleInterface):
        super().__init__(relays)

    def _update_relays(self, state: str, relays: Collection[int]):
        """"""
        pattern = [
            state if i in relays else p
            for i, p in enumerate(self.pattern)
        ]
        self.relays.set_state_of_devices(pattern)
        self.pattern = pattern

    def play(self, pitches: set[int]):
        """"""
        print("play", pitches)
        self._update_relays('1', pitches)

    def release(self, pitches: set[int]):
        """"""
        print("release", pitches)
        self._update_relays('0', pitches)

class DrumSet(RelayInstrument):
    """"""
    accent_levels = 4
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
        self.pattern = new_pattern

    def mirror(self, pattern: str):
        self.relays.set_state_of_devices(pattern)
        self.pattern = pattern

class RestInstrument(Instrument):
    """"""
    def __init__(self):
        super().__init__()

    def play(self):
        raise NotImplementedError
