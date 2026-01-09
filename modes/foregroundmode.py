"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass

from lightset_misc import ALL_HIGH, ALL_ON
from .basemode import BaseMode
from specialparams import SpecialParams

@dataclass
class ForegroundMode(BaseMode, ABC):
    """Base for all Playing and Select modes."""
    special: SpecialParams | None = None

    def __post_init__(self) -> None:
        """Duplicate resource attributes for convenience."""
        self.bells = self.player.bells
        self.buttons = self.player.buttons
        self.drums = self.player.drums
        self.lights = self.player.lights

    @staticmethod
    def wrap_value(
        lower: int,
        upper: int, 
        current: int, 
        delta: int,
    ) -> int:
        """Return current + delta, wrapping the value
           within the inclusive range lower..upper."""
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

    def mode_index(self, current: int, delta: int) -> int:
        """Return a new mode index, wrapping index in both directions."""
        return self.wrap_value(1, max(self.player.modes), current, delta)

