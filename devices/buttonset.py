"""Marquee Lighted Sign Project - buttonset"""

from dataclasses import dataclass, fields
import logging
import threading

from .devices_misc import (
    ButtonAction, ButtonInterface, 
    ButtonPhysicallyChanged, LightedButtonInterface,
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
                button, 'button_action', self.button_activity
            )
        self.reset()

    def button_activity(
        self, 
        button: ButtonInterface, 
        action: ButtonAction,
    ) -> None:
        """Called by Button that had activity."""
        log.info(f"Button <{button}> physically {action}")
        self.button_actioned = button
        self.button_action = action
        self.pressed_event.set()
        
    def reset(self) -> None:
        """Prepare for a button press."""
        self.button_actioned = None
        self.button_action = None
        self.pressed_event = threading.Event()

    def wait(self, seconds: float | None) -> None:
        """Wait until seconds have elapsed or any button is pressed."""
        if self.pressed_event.wait(seconds):
            assert self.button_actioned is not None
            assert self.button_action is not None
            raise ButtonPhysicallyChanged(
                self.button_actioned, self.button_action,
            )

