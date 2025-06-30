"""Marquee Lighted Sign Project - buttons"""

from dataclasses import dataclass
import threading
from typing import ClassVar
from signal import signal

from gpiozero import Button as _Button  # type: ignore

class ButtonPressed(Exception):
    """Button pressed base exception."""

class PhysicalButtonPressed(ButtonPressed):
    """Physical button pressed exception."""

class VirtualButtonPressed(ButtonPressed):
    """Virtual button pressed (IPC signal received) exception."""

@dataclass
class Button:
    """Supports physical buttons on remote and sign."""

    buttons: ClassVar[list["Button"]] = []

    @classmethod
    def reset(cls):
        """Prepare for a button press."""
        print("Button.reset()")
        cls.which_button_pressed: Button | None = None
        cls.pressed_event = threading.Event()

    @classmethod
    def wait(cls, seconds: float | None):
        """Wait until seconds have elapsed or any button is pressed."""
        if cls.pressed_event.wait(seconds):
            raise PhysicalButtonPressed(cls.which_button_pressed)

    button: _Button
    signal_number: int | None = None

    def __post_init__(self):
        """Create a button instance."""
        if not Button.buttons:
            print(f"Initializing buttons")
            Button.reset()
        Button.buttons.append(self)
        self.button.when_pressed = self.button_pressed
        if self.signal_number is not None:
            signal(
                self.signal_number,
                lambda _, __: self.virtual_button_pressed(),
            )
    
    def close(self):
        """Clean up."""
        self.button.close()

    def button_pressed(self):
        """Callback for button press."""
        print(f"Button <{self}> pressed")
        Button.which_button_pressed = self
        Button.pressed_event.set()

    def virtual_button_pressed(self):
        """Callback for virtual button press."""
        print(f"Virtual button <{self}> pressed")
        raise VirtualButtonPressed(self)
