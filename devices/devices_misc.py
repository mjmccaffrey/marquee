"""Marquee Lighted Sign Project - devices_misc"""

from dataclasses import dataclass
from enum import auto, StrEnum
from typing import Protocol


class ButtonRef(StrEnum):
    """Every button."""
    BODY_BACK = auto()
    CORDED_A = auto()
    CORDED_B = auto()
    GAME_START = auto()
    REMOTE_A = auto()
    REMOTE_B = auto()
    REMOTE_C = auto()
    REMOTE_D = auto()

class ButtonAction(StrEnum):
    """"""
    HELD = auto()
    PRESSED = auto()
    RELEASED = auto()

@dataclass
class ButtonActionException(Exception):
    """Button activity base exception."""
    button: ButtonRef
    action: ButtonAction

class ButtonPhysicallyChanged(ButtonActionException):
    """Physical button pressed exception."""

class ButtonVirtuallyPressed(ButtonActionException):
    """Virtual button pressed (IPC signal received) exception."""


class ButtonInterface(Protocol):
    """Button interface."""

    def button_physically_held(self) -> None:
        ...

    def button_physically_pressed(self) -> None:
        ...

    def button_physically_released(self) -> None:
        ...

    def button_virtually_pressed(self, signal_number, stack_frame) -> None:
        ...

    def close(self) -> None:
        ...


class LightedButtonInterface(ButtonInterface):
    """Lighted button interface."""

    def set_light(self, on: bool) -> None:
        ...


class ButtonActionInterface(Protocol):
    """"""
    def __call__(
        self,
        button: ButtonRef,
        action: ButtonAction
    ) -> None:
        ...

