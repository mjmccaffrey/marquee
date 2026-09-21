"""Marquee Lighted Sign Project - button"""

from collections.abc import Callable
from dataclasses import dataclass, field
import logging
import signal
from typing_extensions import override

import gpiozero

from schemas import (
    Control, ControlInterrupt, ControlAction, InterruptSource, Interrupt,
)
from devices.relaymodule import RelayClient

log = logging.getLogger('marquee.' + __name__)


@dataclass
class Button(Control):
    """Supports physical buttons on remote and sign."""
    button: gpiozero.Button
    supports_hold: bool = False
    signal_number: int | None = None
    execute_interrupt: Callable[[Interrupt], None] = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        self.button.when_pressed = self.pressed_via_gpio
        if self.supports_hold:
            self.button.when_held = self.held_via_gpio
        if self.signal_number is not None:
            signal.signal(
                self.signal_number, self.pressed_via_signal,
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

    def held_via_gpio(self) -> None:
        """Callback for button held via gpio."""
        log.info(f"Button <{self}> held via gpio.")
        self.execute_interrupt(
            ControlInterrupt(
                action=ControlAction.BUTTON_HELD,
                control=self.name, 
                source=InterruptSource.GPIO,
            )
        )

    def pressed_via_api(self) -> None:
        """Callback for button pressed via api."""
        log.info(f"Button <{self}> pressed via api.")
        self.execute_interrupt(
            ControlInterrupt(
                action=ControlAction.BUTTON_PRESSED,
                control=self.name, 
                source=InterruptSource.API,
            )
        )

    def pressed_via_gpio(self) -> None:
        """Callback for button pressed via gpio."""
        log.info(f"Button <{self}> pressed via gpio.")
        self.execute_interrupt(
            ControlInterrupt(
                action=ControlAction.BUTTON_PRESSED,
                control=self.name, 
                source=InterruptSource.GPIO,
            )
        )

    def pressed_via_signal(self, signal_number, stack_frame) -> None:
        """Callback for button pressed via signal."""
        log.info(f"Button <{self}> pressed via signal.")
        self.execute_interrupt(
            ControlInterrupt(
                action=ControlAction.BUTTON_PRESSED,
                control=self.name,
                source=InterruptSource.SIGNAL,
            )
        )


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

    @override
    def off(self) -> None:
        """Turn off light."""
        self.set_light(on=False)
        
