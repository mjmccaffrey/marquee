"""Marquee Lighted Sign Project - button"""

import threading
import time

import gpiozero

class ButtonPressed(Exception):
    """Button pressed exception; not an error."""

class Button():
    """Supports the physical mode selection button
       connected to the RPi GPIO controller."""

    def __init__(self):
        """Create the (only) button instance."""
        self._button = gpiozero.Button(pin=4, bounce_time=0.10)
        self.last_pressed = None
        self.reset()

    def _button_pressed_ignore(self):
        """Callback for button press at undesired time."""
        print("Button.button_pressed called - ignoring")

    def _button_pressed_act(self):
        """Callback for button press to change desired mode."""
        print("Button.button_pressed called - acting")
        self.last_pressed = time.time()
        self._pressed_event.set()
        self._button.when_pressed = self._button_pressed_ignore

    def just_pressed(self):
        """Was the button very recently pressed?"""
        return self._pressed_event.is_set()

    def reset(self):
        """Prepare for a valid button press."""
        self._button.when_pressed = self._button_pressed_act
        self._pressed_event = threading.Event()

    def wait(self, seconds=None):
        """Pause the thread until either the seconds have elapsed
           or the button has been pressed."""
        if self._pressed_event.wait(seconds):
            raise ButtonPressed
