""""""

from collections.abc import Callable
from dataclasses import dataclass

@dataclass
class SpecialParams:
    """Base class for special parameters."""

@dataclass
class ActionParams(SpecialParams):
    """Parameters for an arbitrary action."""
    action: Callable

@dataclass
class DimmerParams(SpecialParams):
    """Parameters for using dimmers rather than relays."""
    concurrent: bool = True
    brightness_on: int = 100
    brightness_off: int = 0
    speed_factor: float = 1.0
    transition_on: float | None = 0.5  # !!!! None
    transition_off: float | None = 0.5  # !!!! None
