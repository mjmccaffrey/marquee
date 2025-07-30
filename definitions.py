"""Marquee Lighted Sign Project - definitions"""

from collections.abc import Callable
from dataclasses import dataclass, field

from typing import Any, Type

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
    
@dataclass
class ModeConstructor:
    name: str
    mode_class: Type
    kwargs: dict[str, Any]

@dataclass
class AutoModeEntry:
    index: int
    name: str
    duration: float

class Shutdown(Exception):
    """Triggered to clean up and shut down the system."""
