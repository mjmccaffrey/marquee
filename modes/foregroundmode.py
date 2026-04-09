"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass
import logging

from devices.buttonset import ButtonSet
from devices.specialparams import SpecialParams
from instruments import BellSet, ClickSet, DrumSet, LightSet
from .basemode import BaseMode

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

