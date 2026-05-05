"""Marquee Lighted Sign Project - buttonset"""

from dataclasses import dataclass
import logging
import threading
from typing import cast

from .button import Button, LightedButton
from .devices_misc import ButtonAction, ButtonName, ButtonPhysicallyChanged

log = logging.getLogger('marquee.' + __name__)

@dataclass
class ButtonSet:
    """Every button."""
    body_back: Button
    corded_a: Button
    corded_b: Button
    game_start: LightedButton
    remote_a: Button
    remote_b: Button
    remote_c: Button
    remote_d: Button

    def __post_init__(self):
        """"""
        log.info(f"Initializing buttons")
        for name in ButtonName:
            button = cast(Button, getattr(self, name))
            button.action_in_button_set = self.action_in_button_set
        self.reset()

    def action_in_button_set(
        self, 
        button: ButtonName, 
        action: ButtonAction,
    ) -> None:
        """Called by Button that had action."""
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

