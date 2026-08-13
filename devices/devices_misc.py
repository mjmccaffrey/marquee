"""Marquee Lighted Sign Project - devices_misc"""

from dataclasses import dataclass
from enum import auto, StrEnum


class ControlName(StrEnum):
    """Every control."""
    BODY_BACK = auto()
    BRIGHTNESS = auto()
    CORDED_A = auto()
    CORDED_B = auto()
    CORDED_C = auto()
    GAME_START = auto()
    ROTARY_A = auto()

class ButtonAction(StrEnum):
    """Every button action."""
    HELD = auto()
    PRESSED = auto()
    RELEASED = auto()

@dataclass
class ControlActionException(Exception):
    """Button action base exception."""
    control: ControlName
    action: ButtonAction

class ControlPhysicallyChanged(ControlActionException):
    """Physical button pressed exception."""

class ControlVirtuallyChanged(ControlActionException):
    """Virtual button pressed (IPC signal received) exception."""

