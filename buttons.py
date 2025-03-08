"""Marquee Lighted Sign Project - buttons"""

import signal as _signal
import threading

from gpiozero import Button as _Button  # type: ignore

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
            raise PhysicalButtonPressed(cls._button_pressed)

    def __init__(self, name:str, pin:int, signal=None):
        """Create a button instance."""
        self.name = name
        self.pin = pin
        print(f"Initializing {self}")
        if not Button.buttons:
            Button.reset()
        Button.buttons.append(self)
        self._button: _Button = _Button(pin=self.pin, bounce_time=0.10)
        self._button.when_pressed = self._button_pressed_act
        if signal is not None:
            _signal.signal(
                signal,
                lambda _, __: self.virtual_button_pressed(),
            )

    def __str__(self):
        return f"button '{self.name}' @ {self.pin}"
    
    def __repr__(self):
        return f"<{self}>"
    
    def close(self):
        """Clean up."""
        self._button.close()

    def _button_pressed_ignore(self):
        """Callback for button press at undesired time."""
        print("Button <{self}> pressed - ignoring")

    def _button_pressed_act(self):
        """Callback for button press."""
        print("Button <{self}> pressed - acting")
        Button._button_pressed = self

        self.pressed_event.set()
        self._button.when_pressed = self._button_pressed_ignore

    def virtual_button_pressed(self):
        """Callback for virtual button press."""
        raise VirtualButtonPressed(self)
