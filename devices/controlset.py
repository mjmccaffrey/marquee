"""Marquee Lighted Sign Project - controlset"""

from collections import UserDict
import logging
import threading

from .button import Button
from .device_schemas import (
    Control, ControlAction, ControlName, ControlPhysicallyChanged
)

log = logging.getLogger('marquee.' + __name__)

class ControlSet(UserDict[ControlName, Control], Control):
    """Note: Do not modify the dict after creation."""

    def __init__(self, *args, **kwargs):
        """Initialize control set."""
        log.info(f"Initializing control set")
        super().__init__(*args, **kwargs)
        for control in self.data.values():
            if not isinstance(control, Control):
                raise TypeError(control)
            if isinstance(control, Button):
                control.action_in_control_set = self.action
        self.reset()

    def action(
        self, 
        control: ControlName, 
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

