"""Marquee Lighted Sign Project - selectmode"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .foregroundmode import ForegroundMode
from button import Button
from lightset_misc import ALL_OFF
from mode_misc import ModeIndex
from player import Player
from sequences import rotate_build_flip


@dataclass(kw_only=True)
class SelectMode(ForegroundMode, ABC):
    """Base for the selection modes."""
    player: Player

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
        """Respond to button being pressed.
           Return index of new mode, if any."""
        b = self.buttons
        match button:
            case b.body_back | b.remote_a | b.remote_d:
                self.desired = self.update_desired(+1)
            case b.remote_b:
                self.desired = self.update_desired(-1)
            case b.remote_c:
                self.c_button_pressed()
            case _:
                raise ValueError("Unrecognized button.")
        return None

    def execute(self) -> None:
        """Return user's final selection if made, otherwise None."""
        print(f"SelectMode.execute {self.previous=} {self.desired=}")
        if (    # The desired mode was not changed last go-around.
                self.desired != self.previous_desired 
                # If special mode, change mode immediately.
            and self.desired > 0 
        ):
            # Not last pass.
            # Show user what desired mode number is currently selected.
            print(f"Desired is {self.desired} {self.modes[self.desired].name}")
            self.lights.set_relays(ALL_OFF, special=self.special)
            self.player.create_mode_instance(
                mode_index=ModeIndex.COUNTER,
                parent=self,
                extra_kwargs=dict(
                    sequence=lambda: rotate_build_flip(count=self.desired),
                    pre_delay=0.5,
                    delay=0.20, 
                    repeat=False,
                    special=self.special,
                ),
            ).execute()
            self.previous_desired = self.desired
            self.schedule(self.execute, due_rel=4.0)
        else:
            # Last pass.
            # Time elapsed without a button being pressed.
            # Change the mode.
            self.change_mode(self.desired)

