"""Marquee Lighted Sign Project - select_modes"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import time

from .basemode import BaseMode
from button import Button
from configuration import (
    ALL_OFF, LIGHT_COUNT, SELECT_BRIGHTNESS, SELECT_MODE
)
from sequences import rotate_build_flip

@dataclass(kw_only=True)
class SelectMode(BaseMode, ABC):
    """Supports the selection modes."""

    @abstractmethod
    def __post_init__(self):
        """Initialize."""
        self.preset_devices(dimmers=True)

    def setup(
        self,
        lower: int,
        upper: int,
        previous: int,
    ):
        """Supports modes that allow the user to select a value."""
        self.lower: int = lower
        self.upper: int = upper
        self.previous: int = previous
        self.desired: int = self.previous
        self.previous_desired: int | None = None

    def update_desired(self, delta: int) -> int:
        """Update the current selection, wrapping within the bounds."""
        return self.wrap_value(self.lower, self.upper, self.desired, delta)

    @abstractmethod
    def c_button_pressed(self):
        """Respond to C button press."""

    def button_action(self, button: Button):
        """Respond to button being pressed."""
        new = None
        b = self.player.buttons
        match button:
            case b.body_back | b.remote_a | b.remote_d:
                self.desired = self.update_desired(+1)
            case b.remote_b:
                self.desired = self.update_desired(-1)
            case b.remote_c:
                self.c_button_pressed()
            case _:
                raise ValueError("Unrecognized button.")
        return new

    def execute(self):
        """Return user's final selection if made, otherwise None."""
        new = None
        if self.desired != self.previous_desired:
            # Not last pass.
            # Show user what desired mode number is currently selected.
            print(f"Desired is {self.desired}")
            self.player.lights.set_relays(ALL_OFF, special=self.special)
            time.sleep(0.5)
            self.player.play_sequence(
                rotate_build_flip(count=self.desired),
                pace=0.20, post_delay=4.0,
                special=self.special,
            )
            self.previous_desired = self.desired
        else:
            # Last pass.
            # Time elapsed without a button being pressed.
            # Return the selection.
            new = self.desired
        return new

@dataclass(kw_only=True)
class BrightnessSelectMode(SelectMode):
    """Allows user to select maximum brightness."""

    def __post_init__(self):
        """Initialize."""
        super().__post_init__()
        super().setup(
            lower=1, 
            upper=LIGHT_COUNT,
            previous=6,
        )

    def execute(self):
        """Set current brightness. Return select_mode if 
           final brightness selected, else None."""
        self.player.lights.brightness_factor = self.desired / LIGHT_COUNT
        self.player.lights.set_dimmers(brightnesses=[100] * LIGHT_COUNT)
        new = super().execute()
        if new is not None:  # Selection was made.
            new = SELECT_MODE
        return new

    def c_button_pressed(self):
        """Respond to C button press."""
        print("C button ignored in brightness select mode.")

@dataclass(kw_only=True)
class ModeSelectMode(SelectMode):
    """Allows user to select mode."""

    def __post_init__(self):
        """Initialize."""
        super().__post_init__()
        previous = (
            self.player.remembered_mode
                if self.player.current_mode == SELECT_BRIGHTNESS else
            self.player.current_mode
        )
        assert previous is not None
        assert self.player.current_mode is not None
        super().setup(
            lower=1, 
            upper=max(self.player.modes),
            previous=previous,
        )

    def c_button_pressed(self):
        """Respond to C button press."""
        self.desired = SELECT_BRIGHTNESS
        self.player.remembered_mode = self.previous
