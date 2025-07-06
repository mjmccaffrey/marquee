""""""

from collections.abc import Callable
from dataclasses import dataclass

from typing import Any, Type

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

@dataclass
class ModeConstructor:
    name: str
    mode_class: Type
    kwargs: dict[str, Any]

@dataclass
class AutoModeChangeEntry:
    duration_seconds: int
    mode_index: int
