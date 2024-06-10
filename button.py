# Marquee Lighted Sign Project - button

""" """

import threading
import time

import gpiozero

class ButtonPressed(Exception):
    """ """

class Button():
    """ """

    def __init__(self):
        """ """
        self._button = gpiozero.Button(pin = 4, bounce_time = 0.10)
        self.last_pressed = None
        self.reset()

    def _button_pressed_ignore(self):
        """ """
        print(f"Button.button_pressed called - ignoring")

    def _button_pressed_act(self):
        """ """
        print(f"Button.button_pressed called - acting")
        self.last_pressed = time.time()
        self._pressed_event.set()
        self._button.when_pressed = self._button_pressed_ignore

    def just_pressed(self):
        """ """
        return self._pressed_event.is_set()

    def reset(self):
        """ """
        self._button.when_pressed = self._button_pressed_act
        self._pressed_event = threading.Event()

    def wait(self, seconds = None):
        """ """
        if self._pressed_event.wait(seconds):
            raise ButtonPressed
