"""Marquee Lighted Sign Project - instruments_concrete"""

from collections.abc import Collection
import logging
from typing_extensions import override

from devices.relaymodule import RelayClient
from .instruments_abstract import (
    RelayInstrument, ReleaseableInstrument, DinInstrument,
)

log = logging.getLogger('marquee.' + __name__)


class BellSet(RelayInstrument, ReleaseableInstrument):
    """Set of bells."""
    pitch_levels = 8
    release_time: float = 0.09

    def __init__(self, relays: RelayClient) -> None:
        super().__init__(relays)

    def _update_relays(self, state: str, relays: Collection[int]) -> None:
        """Set relays to state."""
        pattern = ''.join(
            state if i in relays else p
            for i, p in enumerate(self.relays.device_pattern)
        )
        self.relays.set_state_of_devices(pattern)

    @override
    def play(self, pitches: set[int]) -> None:
        """Play specified pitches."""
        self._update_relays('1', pitches)

    @override
    def release(self, pitches: set[int]) -> None:
        """Release specified pitches."""
        self._update_relays('0', pitches)


class DrumSet(RelayInstrument):
    """Set of drums."""
    accent_levels = 4
    accent_to_relay_count = {
        0: 4, 1: 8, 2: 16, 3: 32,
    }
    pitch_levels = 2
    pitch_to_relay_state = {
        0: '0', 1: '1',
    }

    def __init__(self, relays: RelayClient) -> None:
        super().__init__(relays)

    @override
    def play(self, accent: int, pitches: set[int]) -> None:
        """Play specified pitches."""

        def flip(s: str) -> str:
            return '0' if s == '1' else '1'

        new_pattern = self.relays.device_pattern
        desired_count = self.accent_to_relay_count[accent]
        for pitch in pitches:
            desired_state = self.pitch_to_relay_state[pitch]
            selected = self._select_relays(desired_state, desired_count)
            new_pattern = ''.join(
                flip(p) if i in selected else p
                for i, p in enumerate(new_pattern)
            )
        self.relays.set_state_of_devices(new_pattern)


class Ringer(DinInstrument):
    """Rapidly repeating ringer bell."""


class Buzzer(DinInstrument):
    """Simple door buzzer."""

