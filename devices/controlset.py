"""Marquee Lighted Sign Project - controlset"""

from dataclasses import dataclass
import logging
import threading
from typing import cast

import gpiozero

from .button import Button, LightedButton
from .devices_misc import ControlAction, Control, ControlPhysicallyChanged

log = logging.getLogger('marquee.' + __name__)

@dataclass
class ControlSet:
    """Every control."""
    body_back: Button
    corded_a: Button
    corded_b: Button
    corded_c: Button
    game_start: LightedButton
    rotary_a: gpiozero.RotaryEncoder

    def __post_init__(self):
        """Initialize control set."""
        log.info(f"Initializing controls")
        for control in Control:
            if isinstance(control, Button):
                button = cast(Button, getattr(self, control))
                button.action_in_control_set = self.action_in_control_set
        self.reset()

    def action_in_control_set(
        self, 
        control: Control, 
        action: ControlAction,
    ) -> None:
        """Called by Button that had action."""
        log.info(f"Button <{control}> physically {action}")
        self.button_actioned = control
        self.control_action = action
        self.pressed_event.set()
        
    def reset(self) -> None:
        """Prepare for more control activity."""
        self.button_actioned = None
        self.control_action = None
        self.pressed_event = threading.Event()

    def wait(self, seconds: float | None) -> None:
        """Wait until seconds have elapsed or activity on any control."""
        if self.pressed_event.wait(seconds):
            assert self.button_actioned is not None
            assert self.control_action is not None
            raise ControlPhysicallyChanged(
                self.button_actioned, self.control_action,
            )

