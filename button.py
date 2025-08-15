"""Marquee Lighted Sign Project - button"""

from dataclasses import dataclass
import signal
import threading
from typing import ClassVar

from gpiozero import Button as _Button  # type: ignore

from buttoninterface import ButtonInterface

class ButtonPressed(Exception):
    """Button pressed base exception."""

class PhysicalButtonPressed(ButtonPressed):
    """Physical button pressed exception."""

class VirtualButtonPressed(ButtonPressed):
    """Virtual button pressed (IPC signal received) exception."""

class Shutdown(Exception):
    """Triggered to clean up and shut down the system."""

@dataclass
class Button(ButtonInterface):
    """Supports physical buttons on remote and sign."""

    _buttons: ClassVar[list["Button"]] = []
    which_button_pressed: ClassVar["Button | None"]
    button_was_held: ClassVar[bool]
    name: str
    button: _Button
    support_hold: bool = False
    signal_number: int | None = None

    @classmethod
    def reset(cls):
        """Prepare for a button press."""
        # print("Button.reset()")
        cls.which_button_pressed: Button | None = None
        cls.button_was_held = False
        cls.pressed_event = threading.Event()

    @classmethod
    def wait(cls, seconds: float | None):
        """Wait until seconds have elapsed or any button is pressed."""
        if cls.pressed_event.wait(seconds):
            raise PhysicalButtonPressed(
                cls.which_button_pressed, cls.button_was_held,
            )

    def __post_init__(self):
        """Initialize."""
        if not Button._buttons:
            print(f"Initializing buttons")
            Button.reset()
        Button._buttons.append(self)
        self.button.when_pressed = self.button_pressed
        if self.support_hold:
            self.button.when_held = self.button_held
        if self.signal_number is not None:
            signal.signal(
                self.signal_number,
                self.virtual_button_pressed,
            )
    
    def __repr__(self) -> str:
        return f"<{self}>"
    
    def __str__(self) -> str:
        return self.name

    def close(self):
        """Clean up."""
        self.button.close()

    def button_held(self):
        """Callback for button hold."""
        self.button_pressed(held=True)

    def button_pressed(self, held: bool = False):
        """Callback for button press."""
        if held:
            print(f"Button <{self}> held")
        else:
            print(f"Button <{self}> pressed")
        Button.button_was_held = held
        Button.which_button_pressed = self
        Button.pressed_event.set()

    def virtual_button_pressed(self, signal_number, stack_frame):
        """Callback for virtual button press."""
        print(f"Virtual button <{self}> pressed")
        raise VirtualButtonPressed(self)
