# Marquee Lighted Sign Project - button

import gpiozero
import threading
import time

class ButtonPressed(Exception):
    pass

class Button():
    """ """

    def __init__(self):
        self._button = gpiozero.Button(pin = 4, bounce_time = 0.10)
        self.last_pressed = None
        self.reset()

    def _button_pressed_ignore(self):
        print(f"Button.button_pressed called - ignoring ({threading.get_ident()})")

    def _button_pressed_act(self):
        print(f"Button.button_pressed called - acting ({threading.get_ident()})")
        self.last_pressed = time.time()
        self._pressed_event.set()
        self._button.when_pressed = self._button_pressed_ignore
        
    def just_pressed(self):
        return self._pressed_event.is_set()

    def reset(self):
        self._button.when_pressed = self._button_pressed_act
        self._pressed_event = threading.Event()
    
    def wait(self, seconds):
        if self._pressed_event.wait(seconds):
            raise ButtonPressed
