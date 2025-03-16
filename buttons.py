"""Marquee Lighted Sign Project - buttons"""

from gpiozero import Button as _Button  # type: ignore
from signal import signal

import threading

class ButtonPressed(Exception):
    """Button pressed exception; not an error."""

class PhysicalButtonPressed(ButtonPressed):
    """Physical button pressed exception."""

class VirtualButtonPressed(ButtonPressed):
    """Virtual button pressed (IPC signal received) exception."""

class Button:
    """Supports the physical mode selection button
       connected to the RPi GPIO controller."""

    buttons: list["Button"] = []

    @classmethod
    def reset(cls):
        """Prepare for a valid button press."""
        cls._button_pressed: Button | None = None
        cls.pressed_event = threading.Event()
        print("THREADING EVENT CREATED")

    @classmethod
    def wait(cls, seconds: float):
        """"""
        if cls.pressed_event.wait(seconds):
            print(f"Button.wait: {cls._button_pressed} pressed")
            raise PhysicalButtonPressed(cls._button_pressed)

    def __init__(
            self, 
            name: str, 
            button: _Button,
            signal_number: int | None = None,
    ):
        """Create a button instance."""
        self.name = name
        print(f"Initializing {self}")
        if not Button.buttons:
            Button.reset()
        Button.buttons.append(self)
        self._button = button
        self._button.when_pressed = self._button_pressed_act
        if signal_number is not None:
            signal(
                signal_number,
                lambda _, __: self.virtual_button_pressed(),
            )

    def __str__(self):
        return f"button '{self.name}'"
    
    def __repr__(self):
        return f"<{self}>"
    
    def close(self):
        """Clean up."""
        self._button.close()

    def _button_pressed_act(self):
        """Callback for button press."""
        print(f"Button <{self}> pressed - acting")
        Button._button_pressed = self
        self.pressed_event.set()

    def virtual_button_pressed(self):
        """Callback for virtual button press."""
        print(f"Virtual button <{self}> pressed")
        raise VirtualButtonPressed(self)
