"""Marquee Lighted Sign Project - button"""

from dataclasses import dataclass
import logging
import signal

from gpiozero import Button as _Button  # type: ignore

from .devices_misc import ButtonInterface, ButtonVirtuallyPressed

log = logging.getLogger('marquee.button')


@dataclass
class Button(ButtonInterface):
    """Supports physical buttons on remote and sign."""
    name: str
    button: _Button
    support_hold: bool = False
    signal_number: int | None = None
    button_set: ButtonSetInterface | None = None

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
            log.info(f"Button <{self}> held")
        else:
            log.info(f"Button <{self}> pressed")
        self.button_set_pressed(self, held)
        # self.button_set.button_was_held = held
        # self.button_set.which_button_pressed = self
        # self.button_set.pressed_event.set()

    def button_virtually_pressed(self, signal_number, stack_frame) -> None:
        """Callback for virtual button press."""
        log.info(f"Virtual button <{self}> pressed")
        raise ButtonVirtuallyPressed(self)

