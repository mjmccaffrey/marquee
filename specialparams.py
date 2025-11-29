"""Marquee Lighted Sign Project - specialparams"""

from collections.abc import Callable
from dataclasses import dataclass, field

from color import Color

@dataclass
class SpecialParams:
    """Base class for special parameters."""

@dataclass
class ActionParams(SpecialParams):
    """Parameters for an arbitrary action."""
    action: Callable

@dataclass
class BellParams(SpecialParams):
    """Parameters to ring bells."""

@dataclass
class ChannelParams(SpecialParams):
    """Parameters for using channels rather than relays."""
    brightness_on: int = 100
    brightness_off: int = 0
    color_on: Color | None = None
    color_off: Color | None = None
    concurrent: bool = True
    speed_factor: float = 1.0  # ?????
    trans_on: float = 0.5  # ?????
    trans_off: float = 0.5  # ?????

@dataclass
class MirrorParams(SpecialParams):
    """Parameters to mirror lights with another relay board."""
    func: Callable[[str], None] = field(init=False)

