"""Marquee Lighted Sign Project - specialparams"""

from collections.abc import Callable
from dataclasses import dataclass, field


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
class DimmerParams(SpecialParams):
    """Parameters for using dimmers rather than relays."""
    concurrent: bool = True
    brightness_on: int = 100
    brightness_off: int = 0
    speed_factor: float = 1.0
    transition_on: float = 0.5
    transition_off: float = 0.5


@dataclass
class MirrorParams(SpecialParams):
    """Parameters to mirror lights with another relay board."""
    func: Callable[[str], None] = field(init=False)

