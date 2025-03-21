"""Marquee Lighted Sign Project - buttons"""

import threading

from gpiozero import Button as _Button  # type: ignore
from signal import signal

class ButtonPressed(Exception):
    """Button pressed base exception."""

class PhysicalButtonPressed(ButtonPressed):
    """Physical button pressed exception."""

class VirtualButtonPressed(ButtonPressed):
    """Virtual button pressed (IPC signal received) exception."""

class Button:
    """Supports physical buttons on remote and sign."""

    buttons: list["Button"] = []

    @classmethod
    def reset(cls):
        """Prepare for a button press."""
        cls.which_button_pressed: Button | None = None
        cls.pressed_event = threading.Event()

    @classmethod
    def wait(cls, seconds: float | None):
        """Wait until seconds have elapsed or any button is pressed."""
        if cls.pressed_event.wait(seconds):
            raise PhysicalButtonPressed(cls.which_button_pressed)

    def __init__(
            self, 
            name: str, 
            button: _Button,
            signal_number: int | None = None,
    ):
        """Create a button instance."""
        self.name = name
        #print(f"Initializing {self}")
        if not Button.buttons:
            print(f"Initializing buttons")
            Button.reset()
        Button.buttons.append(self)
        self._button = button
        self._button.when_pressed = self.button_pressed
        if signal_number is not None:
            signal(
                signal_number,
                lambda _, __: self.virtual_button_pressed(),
            )

    def __str__(self):
        """"""
        return f"button '{self.name}'"
    
    def __repr__(self):
        """"""
        return f"<{self}>"
    
    def close(self):
        """Clean up."""
        self._button.close()

    def button_pressed(self):
        """Callback for button press."""
        # print(f"Button <{self}> pressed")
        Button.which_button_pressed = self
        Button.pressed_event.set()

    def virtual_button_pressed(self):
        """Callback for virtual button press."""
        print(f"Virtual button <{self}> pressed")
        raise VirtualButtonPressed(self)
