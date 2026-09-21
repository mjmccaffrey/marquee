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


class BaseModeInterface(Protocol):
    """Minimum required of output from create_mode_instance."""
    index: int
    name: str
    serial: int

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

