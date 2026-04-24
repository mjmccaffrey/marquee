"""Marquee Lighted Sign Project - button"""

from dataclasses import dataclass, field
import logging
import signal

from gpiozero import Button as _Button  # type: ignore

from .devices_misc import (
    ButtonAction, ButtonActionInterface, ButtonRef, ButtonVirtuallyPressed
)

log = logging.getLogger('marquee.' + __name__)


@dataclass
class Button(ButtonInterface):
    """Supports physical buttons on remote and sign."""
    name: str
    button: _Button
    supports_hold: bool = False
    supports_release: bool = False
    signal_number: int | None = None
    button_action: ButtonActionInterface = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        self.button.when_pressed = self.button_physically_pressed
        if self.supports_hold:
            self.button.when_held = self.button_physically_held
        if self.supports_release:
            self.button.when_released = self.button_physically_released
        if self.signal_number is not None:
            signal.signal(
                self.signal_number,
                self.button_virtually_pressed,
            )
    
    def __repr__(self) -> str:
        return f"<{self}>"
    
    def __str__(self) -> str:
        return self.name

    def close(self) -> None:
        """Clean up."""
        self.button.close()
        log.info(f"Button {self} closed.")

    def button_physically_held(self) -> None:
        """Callback for physical button hold."""
        self.button_action(self, ButtonAction.HELD)

    def button_physically_pressed(self) -> None:
        """Callback for physical button press."""
        self.button_action(self, ButtonAction.PRESSED)

    def button_physically_released(self) -> None:
        """Callback for physical button release."""
        self.button_action(self, ButtonAction.RELEASED)

    def button_virtually_pressed(self, signal_number, stack_frame) -> None:
        """Callback for virtual button press."""
        log.info(f"Button <{self}> vitually pressed")
        raise ButtonVirtuallyPressed(button=self, action=ButtonAction.PRESSED)

