"""Marquee Lighted Sign Project - devices_misc"""

from dataclasses import dataclass
from enum import auto, StrEnum


class ButtonName(StrEnum):
    """Every button."""
    BODY_BACK = auto()
    CORDED_A = auto()
    CORDED_B = auto()
    CORDED_C = auto()
    GAME_START = auto()
    REMOTE_A = auto()
    REMOTE_B = auto()
    REMOTE_C = auto()
    REMOTE_D = auto()

class ButtonAction(StrEnum):
    """Every button action."""
    HELD = auto()
    PRESSED = auto()
    RELEASED = auto()

@dataclass
class ButtonActionException(Exception):
    """Button action base exception."""
    button: ButtonName
    action: ButtonAction

class ButtonPhysicallyChanged(ButtonActionException):
    """Physical button pressed exception."""

class ButtonVirtuallyPressed(ButtonActionException):
    """Virtual button pressed (IPC signal received) exception."""

