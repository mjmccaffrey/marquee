"""Marquee Lighted Sign Project - buttonset"""

from dataclasses import dataclass, fields
import logging
import threading

from .devices_misc import (
    ButtonInterface, ButtonPhysicallyPressed, LightedButtonInterface,
)

log = logging.getLogger('marquee.' + __name__)


@dataclass
class ButtonSet:
    """Every button."""
    body_back: ButtonInterface
    corded_a: ButtonInterface
    corded_b: ButtonInterface
    game_start: LightedButtonInterface
    remote_a: ButtonInterface
    remote_b: ButtonInterface
    remote_c: ButtonInterface
    remote_d: ButtonInterface

    def __post_init__(self):
        """"""
        log.info(f"Initializing buttons")
        for field in fields(self):
            button = getattr(self, field.name)
            setattr(
                button, 'button_in_set_pressed', self.button_in_set_pressed
            )
        self.reset()

    def button_in_set_pressed(self, button: ButtonInterface, held: bool) -> None:
        """Called by Button that was pressed."""
        self.which_button_pressed = button
        print(button)
        self.button_was_held = held
        self.pressed_event.set()
        
    def reset(self) -> None:
        """Prepare for a button press."""
        self.which_button_pressed = None
        self.button_was_held = False
        self.pressed_event = threading.Event()

    def wait(self, seconds: float | None) -> None:
        """Wait until seconds have elapsed or any button is pressed."""
        if self.pressed_event.wait(seconds):
            assert self.which_button_pressed is not None
            raise ButtonPhysicallyPressed(
                self.which_button_pressed, self.button_was_held,
            )

