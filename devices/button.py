"""Marquee Lighted Sign Project - button"""

from dataclasses import dataclass
import logging
import signal

from gpiozero import Button as _Button  # type: ignore

from .devices_misc import (
    ButtonInSetPressed, ButtonInterface, ButtonVirtuallyPressed
)

log = logging.getLogger('marquee.' + __name__)


@dataclass
class Button(ButtonInterface):
    """Supports physical buttons on remote and sign."""
    name: str
    button: _Button
    support_hold: bool = False
    signal_number: int | None = None
    button_in_set_pressed: ButtonInSetPressed | None = None

    def __post_init__(self) -> None:
        """Initialize."""
        self.button.when_pressed = self.button_physically_pressed
        if self.support_hold:
            self.button.when_held = self.button_physically_held
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
        """Callback for button hold."""
        self.button_physically_pressed(held=True)

    def button_physically_pressed(self, held: bool = False) -> None:
        """Callback for physical button press."""
        if held:
            log.info(f"Button <{self}> physically held")
        else:
            log.info(f"Button <{self}> physically pressed")
        assert self.button_in_set_pressed is not None
        self.button_in_set_pressed(self, held)

    def button_virtually_pressed(self, signal_number, stack_frame) -> None:
        """Callback for virtual button press."""
        log.info(f"Virtual button <{self}> vitually pressed")
        raise ButtonVirtuallyPressed(button=self, held=False)

