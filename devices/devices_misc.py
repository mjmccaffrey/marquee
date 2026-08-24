"""Marquee Lighted Sign Project - devices_misc"""

from dataclasses import dataclass
from enum import auto, StrEnum
from typing import Any


class Control(StrEnum):
    """Every button."""
    BODY_BACK = auto()
    CORDED_A = auto()
    CORDED_B = auto()
    CORDED_C = auto()
    GAME_START = auto()
    ROTARY_A = auto()

class ControlAction(StrEnum):
    """Every control action."""
    BUTTON_HELD = auto()
    BUTTON_PRESSED = auto()
    BUTTON_RELEASED = auto()

class Device(StrEnum):
    """Every device type (only 1 instance of each type)."""
    BELLS = auto()
    CONTROLS = auto()
    DRUMS = auto()
    LIGHTS = auto()
    EXTRA = auto()
    COMBINED = auto()
    CLICKER = auto()
    RINGER = auto()
    BUZZER = auto()
    JOYSTICK = auto()
    TILTS = auto()

DeviceSet = dict[Device, Any]

@dataclass
class ControlActionException(Exception):
    """Button action base exception."""
    control: Control
    action: ControlAction

class ControlPhysicallyChanged(ControlActionException):
    """Physical button pressed exception."""

class ControlVirtuallyChanged(ControlActionException):
    """Virtual button pressed (IPC signal received) exception."""

