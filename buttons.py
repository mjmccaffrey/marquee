"""Marquee Lighted Sign Project - button"""

import signal
import threading

import gpiozero

class ButtonPressed(Exception):
    """Button pressed exception; not an error."""

class PhysicalButtonPressed(ButtonPressed):
    """Physical button pressed exception."""

class VirtualButtonPressed(ButtonPressed):
    """Virtual button pressed (IPC signal received) exception."""

class Button:
    """Supports the physical mode selection button
       connected to the RPi GPIO controller."""

    def __init__(self):
        """Create the (only) button instance."""
        self._button = gpiozero.Button(pin=4, bounce_time=0.10)
        self.reset()
        signal.signal(
            signal.SIGUSR1,  # pylint: disable=no-member
            lambda _, __: self.virtual_button_pressed(),
        )

    def close(self):
        """Clean up."""
        self._button.close()

    def _button_pressed_ignore(self):
        """Callback for button press at undesired time."""

    def _button_pressed_act(self):
        """Callback for button press to change desired mode."""
        self.pressed_event.set()
        self._button.when_pressed = self._button_pressed_ignore

    def reset(self):
        """Prepare for a valid button press."""
        self._button.when_pressed = self._button_pressed_act
        self.pressed_event = threading.Event()

    def virtual_button_pressed(self):
        """Callback for virtual button press (SIGUSR1 received)."""
        raise VirtualButtonPressed
