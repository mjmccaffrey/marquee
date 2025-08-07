"""Marquee Lighted Sign Project - instruments"""

from abc import ABC, abstractmethod
from collections.abc import Collection
import random

from relays import RelayModuleInterface
from sequences import opposite

class Instrument(ABC):
    """Base class for an instrument."""
    accent_levels = 0
    pitch_levels = 0

    def __init__(self):
        super().__init__()

    @abstractmethod
    def play(self):
        """Play specified pitches."""

class ActionInstrument(Instrument, ABC):
    """Conceptual instrument that executes arbitrary actions."""

class RestInstrument(Instrument, ABC):
    """Conceptual instrument that executes rests."""

class RelayInstrument(Instrument, ABC):
    """Abstract instrument that uses relays."""
    def __init__(self, relays: RelayModuleInterface):
        super().__init__()
        self.relays = relays
        self.count = self.relays.relay_count
        self.relays.set_state_of_devices("0" * self.count)
        self.pattern = self.relays.get_state_of_devices()
        assert self.pattern == "0" * self.count

    def select_relays(self, state: str, count: int) -> set[int]:
        """Randomly select count relays in state."""
        candidates = [
            i
            for i, p in enumerate(self.pattern)
            if p == state
        ]
        try:
            selected = set(random.sample(candidates, count))
        except ValueError:
            print(f'{len(candidates)} of {count} {state} relays present.')
            selected = set(candidates)
        return selected

class ReleaseableInstrument(Instrument, ABC):
    """Abstract instrument that has releaseable notes."""
    release_time: float  # Abstract

class BellSet(RelayInstrument, ReleaseableInstrument):
    """Set of bells."""
    pitch_levels = 8
    release_time = 0.09

    def __init__(self, relays: RelayModuleInterface):
        super().__init__(relays)

    def _update_relays(self, state: str, relays: Collection[int]):
        """Set relays to state."""
        pattern = [
            state if i in relays else p
            for i, p in enumerate(self.pattern)
        ]
        self.relays.set_state_of_devices(pattern)
        self.pattern = pattern

    def play(self, pitches: set[int]):
        """Play specified pitches."""
        self._update_relays('1', pitches)

    def release(self, pitches: set[int]):
        """Release specified pitches."""
        self._update_relays('0', pitches)

class DrumSet(RelayInstrument):
    """Set of drums."""
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
        """Play specified pitches."""
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
