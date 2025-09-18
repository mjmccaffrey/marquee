"""Marquee Lighted Sign Project - player"""

from collections.abc import Iterable
from dataclasses import dataclass
import itertools
import time
from typing import Any

from button import Button, ButtonPressed, Shutdown
from modes.automode import AutoMode
from modes.basemode import BaseMode
from modes.modeinterface import ModeInterface
from specialparams import ActionParams, DimmerParams, SpecialParams

from playerinterface import PlayerInterface

class AutoModeDue(Exception):
    """Automatic mode change due exception."""

@dataclass
class Player(PlayerInterface):
    """Executes one mode at a time."""

    def __post_init__(self) -> None:
        """Initialize."""
        print("Initializing player")
        self.auto_mode = None
        self.current_mode = None
        self.remembered_mode = None
        self.pace = 0.0
        self.release_queue = []

    def close(self) -> None:
        """Clean up."""
        print(f"Player {self} closed.")

    def replace_kwarg_values(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Replace variables with current runtime values."""
        vars = {
            'LIGHT_PATTERN': self.lights.relay_pattern,
            'PREVIOUS_MODE': self.current_mode,
        }
        return {
            k: vars[v] if isinstance(v, str) and v in vars else v
            for k, v in kwargs.items()
        }

    def execute(self, starting_mode_index: int) -> None:
        """Play the specified mode and all subsequently selected modes."""
        new_mode = starting_mode_index
        while True:
            mode = self.modes[new_mode]
            mode_instance = mode.mode_class(
                player=self, 
                name=mode.name, 
                **self.replace_kwarg_values(mode.kwargs),
            )
            if isinstance(mode_instance, AutoMode):
                self.auto_mode = mode_instance
            self.current_mode = new_mode
            print(f"Executing mode {self.current_mode} {mode.name}")
            new_mode = self._play_mode_until_changed(mode_instance)

    def _play_mode_until_changed(self, mode: ModeInterface) -> None:
        """Play the specified mode until another mode is selected,
           either by the user or automatically.
           Shut down the system if the (body_back) button is held."""
        new_mode = None
        while new_mode is None:
            try:
                new_mode = mode.execute()
            except ButtonPressed as press:
                # print("ButtonPressed caught")
                button, held = press.args
                if held:
                    raise Shutdown("Button was held.")
                Button.reset()
                assert isinstance(mode, BaseMode)
                new_mode = mode.button_action(button)
            except AutoModeDue:
                print("AutoModeDue caught")
                assert self.auto_mode is not None
                new_mode = self.auto_mode.next_mode()
        return new_mode

    def play_sequence(
            self, 
            sequence: Iterable, 
            count: int = 1, 
            pace: Iterable[float | None] | float | None = None,
            stop: int | None = None, 
            post_delay: float | None = 0.0,
            special: SpecialParams | None = None,
        ) -> None:
        """Execute sequence count times, with pace seconds in between.
           If stop is specified, end the sequence 
           just before the nth pattern.
           Pause for post_delay seconds before exiting."""
        if isinstance(pace, Iterable):
            pace_iter = itertools.cycle(pace)
        else:
            pace_iter = itertools.repeat(pace)
        for _ in range(count):
            for i, lights in enumerate(sequence):
                if stop is not None and i == stop:
                    break
                p = next(pace_iter)
                before = time.time()
                if p is not None:
                    if isinstance(special, DimmerParams):
                        special.speed_factor = self.speed_factor
                if isinstance(special, ActionParams):
                    special.action(lights)
                else:
                    self.lights.set_relays(
                        lights, 
                        special=special,
                    )
                after = time.time()
                self.wait(p, after - before)
        self.wait(post_delay)

    def wait(self, seconds: float | None, elapsed: float = 0) -> None:
        """Wait seconds after adjusting for
           speed_factor and time already elapsed."""
        if (self.auto_mode is not None and
            self.auto_mode.trigger_time < time.time()
        ):
            raise AutoModeDue
        if seconds is None:
            duration = None
        else:
            duration = seconds * self.speed_factor - elapsed
            if duration <= 0:
                # print("!!!!!", seconds, elapsed, duration)
                return
        Button.wait(duration)

    def click(self) -> None:
        """Click the specified otherwise unused light relays."""

        extra = ''.join(
            '0' if e == '1' else '1'
            for e in self.lights.extra_pattern
        )
        self.lights.set_relays(
            light_pattern=self.lights.relay_pattern, 
            extra_pattern=extra,
        )
