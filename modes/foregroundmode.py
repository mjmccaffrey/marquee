"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass
import logging

from devices.buttonset import ButtonSet
from instruments import BellSet, DrumSet
from instruments import ClickSet, LightSet
from .basemode import BaseMode
from devices.specialparams import SpecialParams

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ForegroundMode(BaseMode, ABC):
    """Base for all Playing and Select modes."""
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    top: LightSet
    clicker: ClickSet
    speed_factor: float
    special: SpecialParams | None = None
    reset_lights: bool = True

    def __post_init__(self) -> None:
        """Initialize."""
        log.info("^^^^^^^^^^^^^^^^ FG MODE RESET ^^^^^^^^^^^^^^")
        if self.reset_lights:
            self.lights.reset()

