"""Marquee Lighted Sign Project - button"""

from dataclasses import dataclass, field
import logging
import signal
from typing import Protocol
from typing_extensions import override

import gpiozero

from .device_schemas import (
    Control, ControlAction, ControlName, ControlVirtuallyChanged
)
from devices.relaymodule import RelayClient

log = logging.getLogger('marquee.' + __name__)


@dataclass
class Button(Control):
    """Supports physical buttons on remote and sign."""
    button: gpiozero.Button
    supports_hold: bool = False
    supports_release: bool = False
    signal_number: int | None = None
    action_in_control_set: 'ButtonActionInterface' = field(init=False)

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
    
    @override
    def __repr__(self) -> str:
        return f"<{self}>"
    
    @override
    def __str__(self) -> str:
        return self.name

    def close(self) -> None:
        """Clean up."""
        self.button.close()
        log.info(f"Button {self} closed.")

    def button_physically_held(self) -> None:
        """Callback for physical button hold."""
        self.action_in_control_set(self.name, ControlAction.BUTTON_HELD)

    def button_physically_pressed(self) -> None:
        """Callback for physical button press."""
        self.action_in_control_set(self.name, ControlAction.BUTTON_PRESSED)

    def button_physically_released(self) -> None:
        """Callback for physical button release."""
        self.action_in_control_set(self.name, ControlAction.BUTTON_RELEASED)

    def button_virtually_pressed(self, signal_number, stack_frame) -> None:
        """Callback for virtual button press."""
        log.info(f"Button <{self}> vitually pressed")
        raise ControlVirtuallyChanged(control=self.name, action=ControlAction.BUTTON_PRESSED)


@dataclass(kw_only=True)
class LightedButton(Button):
    """Supports lighted physical buttons."""
    relay: RelayClient
    
    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.set_light(False)

    def set_light(self, on: bool) -> None:
        """Set state of light."""
        self.relay.set_state_of_devices('1' if on else '0')


class ButtonActionInterface(Protocol):
    """Signature for button to call button set upon action."""
    def __call__(
        self,
        control: ControlName,
        action: ControlAction
    ) -> None:
        ...

