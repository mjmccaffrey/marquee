"""Marquee Lighted Sign Project - device_schemas"""

from abc import ABC
from dataclasses import dataclass
from enum import auto, StrEnum


class ControlAction(StrEnum):
    """Every control action."""
    BUTTON_HELD = auto()
    BUTTON_PRESSED = auto()
    BUTTON_RELEASED = auto()

class ControlName(StrEnum):
    """Every button."""
    BODY_BACK = auto()
    CORDED_A = auto()
    CORDED_B = auto()
    CORDED_C = auto()
    GAME_START = auto()
    JOYSTICK = auto()
    ROTARY_A = auto()

class Device(ABC):
    """"""

class DeviceName(StrEnum):
    """Every device type (only 1 instance of each type)."""
    BELLS = auto()
    CONTROLS = auto()
    DRUMS = auto()
    LIGHTS = auto()
    CLICKER = auto()
    RINGER = auto()
    BUZZER = auto()
    JOYSTICK = auto()
    TILTS = auto()

DeviceSet = dict[DeviceName, Device]

@dataclass
class Control(Device, ABC):
    """"""
    name: ControlName

@dataclass
class ControlActionException(Exception):
    """Button action base exception."""
    control: ControlName
    action: ControlAction

class ControlPhysicallyChanged(ControlActionException):
    """Physical button pressed exception."""

class ControlVirtuallyChanged(ControlActionException):
    """Virtual button pressed (IPC signal received) exception."""

