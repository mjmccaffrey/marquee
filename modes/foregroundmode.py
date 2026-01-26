"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass

from button_misc import ButtonSet
from instruments import BellSet, DrumSet
from lightset import LightSet
from .basemode import BaseMode
from specialparams import SpecialParams


@dataclass(kw_only=True)
class ForegroundMode(BaseMode, ABC):
    """Base for all Playing and Select modes."""
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    speed_factor: float
    special: SpecialParams | None = None
    reset_lights: bool = True

    def __post_init__(self) -> None:
        """Initialize."""
        if self.reset_lights:
            self.lights.reset()

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
        return self.wrap_value(1, max(self.modes), current, delta)

