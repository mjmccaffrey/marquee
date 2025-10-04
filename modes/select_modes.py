"""Marquee Lighted Sign Project - select_modes"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import time

from .foregroundmode import ForegroundMode
from .mode_misc import ModeIndex
from .playsequencemode import PlaySequenceMode
from button import Button
from lightset_misc import ALL_OFF, LIGHT_COUNT
from player import Player
from sequences import rotate_build_flip


@dataclass(kw_only=True)
class SelectMode(ForegroundMode, ABC):
    """Supports the selection modes."""
    player: Player

    @abstractmethod
    def __post_init__(self) -> None:
        """Initialize."""
        # Do not self.preset_devices(dimmers=True)

    def setup(
        self,
        lower: int,
        upper: int,
        previous: int,
    ) -> None:
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
    def c_button_pressed(self) -> None:
        """Respond to C button press."""

    def button_action(self, button: Button) -> None:
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

    def execute(self) -> int | None:
        """Return user's final selection if made, otherwise None."""
        new = None
        if self.desired != self.previous_desired and self.desired > 0:
            # Not last pass.
            # Show user what desired mode number is currently selected.
            print(f"Desired is {self.desired} {self.player.modes[self.desired].name}")
            self.player.lights.set_relays(ALL_OFF, special=self.special)
            time.sleep(0.5)
            PlaySequenceMode(
                player=self.player,
                name="SelectMode sequence player",
                sequence=lambda: rotate_build_flip(count=self.desired),
                delay=0.20, 
                special=self.special,
            ).play()
            self.player.wait(4.0)
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

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        super().setup(
            lower=1, 
            upper=LIGHT_COUNT,
            previous=6,
        )

    def execute(self) -> int | None:
        """Set current brightness. Return select_mode if 
           final brightness selected, else None."""
        self.player.lights.brightness_factor = self.desired / LIGHT_COUNT
        # * make brightness_factor a property that outputs new value
        # * all methods must honor brightness_factor
        self.player.lights.set_dimmers(brightnesses=[100] * LIGHT_COUNT)
        new = super().execute()
        if new is not None:  # Selection was made.
            new = ModeIndex.SELECT_MODE
        return new

    def c_button_pressed(self) -> None:
        """Respond to C button press."""
        print("C button ignored in brightness select mode.")


@dataclass(kw_only=True)
class ModeSelectMode(SelectMode):
    """Allows user to select mode."""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        previous = (
            self.player.remembered_mode
                if self.player.current_mode == ModeIndex.SELECT_BRIGHTNESS else
            self.player.current_mode
        )
        assert previous is not None
        assert self.player.current_mode is not None
        super().setup(
            lower=1, 
            upper=max(self.player.modes),
            previous=previous,
        )

    def c_button_pressed(self) -> None:
        """Respond to C button press."""
        self.desired = ModeIndex.SELECT_BRIGHTNESS
        self.player.remembered_mode = self.previous

