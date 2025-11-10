"""Marquee Lighted Sign Project - player"""

from dataclasses import dataclass, field
import time
from typing import Any, NoReturn

from button import Button, ButtonPressed, Shutdown
from event import Event, PriorityQueue
from modes.background_modes import BackgroundMode
from modes.foregroundmode import ForegroundMode
from modes.modeinterface import ModeInterface
from modes.mode_misc import ChangeMode
from playerinterface import PlayerInterface


@dataclass(repr=False)
class Player(PlayerInterface):
    """Executes one mode at a time. Contains the event queue."""
    event_queue: PriorityQueue = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        print("Initializing player")
        self.fg_mode_history: list[int] = []
        self.bg_mode_instances: dict[int, BackgroundMode] = {}
        self.event_queue = PriorityQueue()

    def __repr__(self) -> str:
        return "Player repr"
    
    def __str__(self) -> str:
        return "Player str"
    
    def close(self) -> None:
        """Clean up."""
        print(f"Player {self} closed.")

    def replace_kwarg_values(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Replace variables with current runtime values."""
        vars = {
            'LIGHT_PATTERN': self.lights.relay_pattern,
            # 'PREVIOUS_MODE': self.current_mode,
        }
        return {
            k: vars[v] if isinstance(v, str) and v in vars else v
            for k, v in kwargs.items()
        }

    def delete_mode_instance(
        self, 
        bg_index: int | None = None,
        fg_instance: ForegroundMode | None = None,
    ) -> None:
        """Delete foreground or background mode instance and scheduled events."""
        assert (bg_index is None) ^ (fg_instance is None)
        if bg_index is not None:
            instance = self.bg_mode_instances.pop(bg_index)
        else:
            instance = fg_instance
        self.event_queue.delete_owned_by(instance)

    def execute(self, starting_mode_index: int) -> None:
        """Play starting_mode and all subsequent modes,
           instantiating and cleaning up each mode as needed."""
        new_mode_index = starting_mode_index
        while True:
            assert new_mode_index is not None
            mode = self.modes[new_mode_index]

            if mode.index in self.bg_mode_instances:
                self.delete_mode_instance(bg_index=mode.index)

            mode_instance = mode.cls(
                player=self,
                index=mode.index,
                name=mode.name, 
                **self.replace_kwarg_values(mode.kwargs),
            )
            if isinstance(mode_instance, BackgroundMode):
                self.bg_mode_instances[mode.index] = mode_instance
            else:
                self.fg_mode_history.append(mode.index)
            new_mode_index = self._play_mode_until_changed(mode_instance)
            if isinstance(mode_instance, ForegroundMode):
                self.delete_mode_instance(fg_instance=mode_instance)

    def _notify_button_action(
        self, 
        current_mode: ModeInterface, 
        button: Button
    ) -> int | None:
        """Notify all background modes, and foreground mode, 
           of button action."""
        for mode in self.bg_mode_instances.values():
            mode.button_action(button)
        return current_mode.button_action(button)

    def _play_mode_until_changed(self, mode: ModeInterface) -> int | None:
        """Play the specified mode until another mode is selected,
           either by the user or automatically.
           Shut down the system if the (body_back) button is held."""
        print(f"Executing mode {mode.index} {mode.name}")
        new_mode = None
        while new_mode is None:
            print(f"{new_mode=}")
            try:
                new_mode = mode.execute()
                self.wait()
            except ButtonPressed as press:
                button, held = press.args
                if held:
                    raise Shutdown("Button was held.")
                Button.reset()
                print(f"Button {button} pressed in mode {mode.name}")
                new_mode = self._notify_button_action(mode, button)
            except ChangeMode as change_mode:
                print("ChangeMode caught")
                new_mode, = change_mode.args
        return new_mode

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

    def wait(
        self, 
        seconds: float | None = None, 
        elapsed: float = 0.0,
    ) -> None | NoReturn:
        """Wait seconds, after adjusting for
           speed_factor and time already elapsed.
           If seconds is None, wait indefinitely (in this case,
           the current mode instance will never be returned to).
           While waiting, trigger any events that come due; 
           any button press will terminate waiting."""
        now: float
        remaining: float
        start: float
        end: float

        def next_event_or_wait() -> tuple[Event | None, float | None]:
            """Return the next event if it is due, 
               otherwise return seconds to wait."""
            if self.event_queue:
                event = self.event_queue.peek()
                if event.due < now:
                    print(f"Running {event} {now - event.due} late")
                    self.event_queue.pop()
                    return event, 0
                elif seconds is None or event.due < end:
                    print(f"Waiting for {event} or button push")
                    return None, event.due - now
                else:
                    print(f"Waiting for remaining {remaining} or button push; queue not empty")
                    return None, remaining
            else:
                if seconds is None:
                    print(f"Waiting for button push")
                    return None, None
                else:
                    print(f"Waiting for remaining {remaining} or button push; queue empty")
                    return None, remaining

        print(f"Wait {seconds}, {elapsed}")
        if seconds is not None:
            seconds *= self.speed_factor
        start = time.time()
        while True:
            now = time.time()
            if seconds is not None:
                remaining = start + seconds - elapsed - now
                end = now + remaining
                if now > end:
                    print(f"Exiting wait {now - end} late")
                    break
            event, duration = next_event_or_wait()
            if event is not None:
                event.action()
                print("Action executed")
            else:
                Button.wait(duration)

