"""Marquee Lighted Sign Project - specialparams"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar, Self

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
    trans_on: float = 0.5  # ?????
    trans_off: float = 0.5  # ?????
    generate: Callable[[], Self] | None = None

@dataclass
class MirrorParams(SpecialParams):
    """Parameters to mirror lights with another relay board."""
    mirror: ClassVar[Callable[[str], None]]

@dataclass
class EmulateParams(ChannelParams, MirrorParams):
    """Emulate relay experience when using smart bulbs."""
    trans_on: ClassVar[float] = 0.0
    trans_off: ClassVar[float] = 0.0

