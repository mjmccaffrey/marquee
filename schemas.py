"""Marquee Lighted Sign Project - schemas"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import auto, IntEnum, StrEnum
from typing import Any, Callable, Protocol
from typing_extensions import override


class Device(ABC):
    """"""
    @abstractmethod
    def off(self) -> None:
        """Turn off device to the extent possible."""


class ButtonName(StrEnum):
    """Every button."""
    REAR = auto()
    CORDED_A = auto()
    CORDED_B = auto()
    GAME_START = auto()


class ControlName(StrEnum):
    """Every control."""
    BUTTON_REAR = auto()
    BUTTON_CORDED_A = auto()
    BUTTON_CORDED_B = auto()
    BUTTON_GAME_START = auto()
    JOYSTICK = auto()
    TILTS = auto()


class InstrumentName(StrEnum):
    """Every instrument."""
    BELLS = auto()
    BUZZER = auto()
    CLICKER = auto()
    DRUMS = auto()
    LIGHTS = auto()
    RINGER = auto()


class DeviceName(StrEnum):
    """Every device (controls | instruments)."""
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

    @override
    def off(self) -> None:
        """Do nothing; most controls cannot turn off."""


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
    control: ControlName


@dataclass
class Exit(Exception):
    shutdown: bool


@dataclass
class CycleEntry:
    name: str | None
    seconds: float | None
    index: int | None = None


CycleSequence = list[tuple[str, int | None]]


class BaseModeInterface(Protocol):
    """Interface to BaseMode."""
    background: bool
    index: int
    name: str
    parent: 'BaseModeInterface | None'
    serial: int

    def close(self) -> None: ...

    def command_action(self, command: APICommand) -> bool: ...

    def control_action(self, control: ControlName) -> bool: ...

    def execute(self) -> None: ...


@dataclass(kw_only=True)
class ModeDefinition:
    index: int | None = None
    name: str
    cls: type[BaseModeInterface]
    kwargs: dict[str, Any] = field(default_factory=dict)


class ModeIndex(IntEnum):
    MODE_SELECT = 0
    DEFAULT = 1

