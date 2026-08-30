"""Marquee Lighted Sign Project - instruments_abstract"""

from abc import ABC, abstractmethod
import logging
import random
from typing_extensions import override

from devices.device_schemas import Device, DeviceName
from devices.relaymodule import RelayClient

log = logging.getLogger('marquee.' + __name__)


class Instrument(Device, ABC):
    """Base class for an instrument."""
    device: DeviceName
    accent_levels = 0
    pitch_levels = 0

    def __init__(self) -> None:
        super().__init__()

    def close(self) -> None:
        """Close."""
        log.info(f"Instrument {self} closed.")

    @abstractmethod
    def play(self) -> None:
        """Play specified pitches."""


class LightChannelInstrument(Instrument, ABC):
    """Conceptual instrument that executes light channel actions."""


class LightRelayInstrument(Instrument, ABC):
    """Conceptual instrument that executes light relay actions."""


class RelayInstrument(Instrument, ABC):
    """Abstract instrument that uses relays."""
    def __init__(self, relays: RelayClient) -> None:
        super().__init__()
        self.relays = relays
        self.count = self.relays.count
        self.relays.set_state_of_devices("0" * self.count)
        assert self.relays.device_pattern == "0" * self.count

    @override
    def close(self) -> None:
        """Close."""
        self.relays.set_state_of_devices("0" * self.count)
        super().close()

    def _select_relays(self, state: str, count: int) -> set[int]:
        """Randomly select count relays in state."""
        candidates = [
            i
            for i, p in enumerate(self.relays.device_pattern)
            if p == state
        ]
        try:
            selected = set(random.sample(candidates, count))
        except ValueError:
            log.info(f'Using only {len(candidates)} of {count} {state} relays desired.')
            selected = set(candidates)
        return selected


class ReleaseableInstrument(Instrument, ABC):
    """Abstract instrument that has releaseable notes."""

    def release(self) -> None:
        """Release specified pitches."""


class DinInstrument(RelayInstrument, ReleaseableInstrument, ABC):
    """Simple sustained noise instrument."""
    pitch_levels = 1

    @override
    def play(self) -> None:
        """"""
        self.relays.set_state_of_devices("1")

    @override
    def release(self) -> None:
        """"""
        self.relays.set_state_of_devices("0")

    def rest(self) -> None:
        """"""
        self.release()

