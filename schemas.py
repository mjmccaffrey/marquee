"""Marquee Lighted Sign Project - schemas"""

from abc import ABC
from dataclasses import dataclass, field
from enum import auto, IntEnum, StrEnum
from typing import Any, Callable, NotRequired, TypedDict

from devices.button import Button
from devices.joystick import Joystick
from devices.tiltset import TiltSet
from instruments import (
    BellSet, Buzzer, Clicker, DrumSet, LightSet, Ringer,
)


class Device(ABC):
    """"""


class DeviceName(StrEnum):
    """Every device."""
    BELLS = auto()
    BUTTON_REAR = auto()
    BUTTON_CORDED_A = auto()
    BUTTON_CORDED_B = auto()
    BUTTON_GAME_START = auto()
    BUZZER = auto()
    CLICKER = auto()
    DRUMS = auto()
    JOYSTICK = auto()
    LIGHTS = auto()
    RINGER = auto()
    TILTS = auto()


class DeviceSet(TypedDict, closed=True):
    button_rear: Button
    button_corded_a: Button
    button_corded_b: Button
    button_game_start: NotRequired[Button]
    buzzer: NotRequired[Buzzer]
    clicker: Clicker
    drums: DrumSet
    joystick: NotRequired[Joystick]
    lights: LightSet
    ringer: NotRequired[Ringer]
    tilts: NotRequired[TiltSet]


class APICommand(StrEnum):
    """"""
    NEXT_ENTRY = auto()
    PREVIOUS_ENTRY = auto()
    NEXT_MODE = auto()
    PREVIOUS_MODE = auto()


@dataclass
class Control(Device, ABC):
    """"""
    name: DeviceName
    execute_interrupt: Callable = field(init=False)


class ControlAction(StrEnum):
    """Every control action."""
    BUTTON_HELD = auto()
    BUTTON_PRESSED = auto()


class InterruptSource(StrEnum):
    """Every control action source."""
    API = auto()
    GPIO = auto()
    MODE = auto()
    SIGNAL = auto()


@dataclass
class Interrupt(Exception, ABC):
    """"""
    source: InterruptSource


@dataclass
class CommandInterrupt(Interrupt):
    """"""
    command: APICommand


@dataclass
class ChangeModeInterrupt(Interrupt):
    """"""
    mode_index: int


@dataclass
class ControlInterrupt(Interrupt):
    """"""
    action: ControlAction
    control: DeviceName


@dataclass
class Exit(Exception):
    shutdown: bool


@dataclass
class CycleEntry:
    name: str
    seconds: float | None
    index: int = -1


CycleSequence = list[tuple[str, int | None]]


@dataclass(kw_only=True)
class ModeDefinition:
    index: int | None = None
    name: str
    cls: type  # !!!
    kwargs: dict[str, Any] = field(default_factory=dict)


class ModeIndex(IntEnum):
    MODE_SELECT = 0
    DEFAULT = 1

