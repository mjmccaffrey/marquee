"""Marquee Lighted Sign Project - players"""

from collections.abc import Iterable
from dataclasses import dataclass
import itertools
import time
from typing import Any

from basemode import AutoMode, BaseMode
from definitions import ActionParams, DimmerParams, SpecialParams, Shutdown
from modes import Mode
from buttons import Button, ButtonPressed

from player_interface import PlayerInterface

class AutoModeDue(Exception):
    """Automatic mode change due exception."""

@dataclass
class Player(PlayerInterface):
    """Executes one mode at a time."""

    def __post_init__(self):
        """Set up initial state."""
        print("Initializing player")
        self.auto_mode = None
        self.current_mode = -1
        self.pace = 0.0

    def close(self):
        """Clean up."""
        try:
            # for button in self.buttons:
            #   button.close()
            pass
        except Exception as e:
            print(e)
        try:
            # !!! self.lights.close()
            pass
        except Exception as e:
            print(e)

    def replace_kwarg_values(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Replace variables with current runtime values."""
        new = {}
        for k, v in kwargs.items():
            match v:
                case 'LIGHT_PATTERN':
                    new[k] = self.lights.relay_pattern
                case 'PREVIOUS_MODE':
                    new[k] = self.current_mode
                case _:
                    new[k] = v
        return new        

    def execute(self, starting_mode_index: int):
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
            if new_mode == 222:
                new_mode = self.mode_ids['section_1']

    def _play_mode_until_changed(self, mode: BaseMode):
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
                assert isinstance(mode, Mode)
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
        ):
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

    def wait(self, seconds: float | None, elapsed: float = 0):
        """Wait the specified seconds after adjusting for
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

    def _flip_extra_relays(self, *indices: int):
        """"""
        def flip(s):
            return '0' if s == '1' else '1'
        assert all(0 <= i < len(self.lights.extra_pattern) for i in indices)
        extra = ''.join(
            flip(e) if i in indices else e
            for i, e in enumerate(self.lights.extra_pattern)
        )
        self.lights.set_relays(
            light_pattern=self.lights.relay_pattern, 
            extra_pattern=extra,
        )

    def click(self):
        """Generate a small click sound by flipping
           an otherwise unused relay."""
        self._flip_extra_relays(0, 1, 2, 3)
