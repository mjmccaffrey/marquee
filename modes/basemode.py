"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass
from typing import Any, Type

from configuration import ALL_HIGH, ALL_ON
from dataclasses import dataclass
from .modeinterface import ModeInterface
from playerinterface import PlayerInterface
from specialparams import MirrorParams, SpecialParams

@dataclass
class ModeConstructor:
    name: str
    mode_class: Type
    kwargs: dict[str, Any]

@dataclass
class BaseMode(ModeInterface, ABC):
    """Base for all Playing modes and the Select mode."""
    player: PlayerInterface
    special: SpecialParams | None = None

    def preset_devices(self, dimmers: bool = False, relays: bool = False):
        """Preset the dimmers and relays as specified."""
        if isinstance(self.special, MirrorParams):
            self.special.func = self.player.drums.mirror
        if dimmers:
            print("Presetting DIMMERS")
            self.player.lights.set_dimmers(ALL_HIGH, force_update=True)
        if relays:
            print("Presetting RELAYS")
            self.player.lights.set_relays(ALL_ON)

    @staticmethod
    def wrap_value(
        lower: int,
        upper: int, 
        current: int, 
        delta: int,
    ):
        """"""
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

    def mode_index(self, current: int, delta: int) -> int:
        """Return a new mode index, wrapping index in both directions."""
        return self.wrap_value(1, max(self.player.modes), current, delta)
