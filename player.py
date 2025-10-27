"""Marquee Lighted Sign Project - player"""

from dataclasses import dataclass, field
import time
from typing import Any, NoReturn

from button import Button, ButtonPressed, Shutdown
from event import PriorityQueue
from modes.background_modes import BackgroundMode
from modes.modeinterface import ModeInterface
from modes.mode_misc import ChangeMode
from playerinterface import PlayerInterface


@dataclass
class Player(PlayerInterface):
    """Executes one mode at a time."""
    event_queue: PriorityQueue = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        print("Initializing player")
        self.current_mode = None
        self.remembered_mode = None
        self.pace = 0.0
        self.bg_mode_instances: dict[int, BackgroundMode] = {}
        self.event_queue = PriorityQueue()

    def close(self) -> None:
        """Clean up."""
        print(f"Player {self} closed.")

    # DELETE
    # def add_event(self, due: float, owner: object, action: Callable) -> None:
    #     """Add event to queue."""
    #     self.event_queue.push(
    #         Event(
    #             due=due,
    #             owner=owner,
    #             action=action,
    #         )
    #     )

    def find_bg_mode(
        self, 
        mtype: type[BackgroundMode],
    ) -> int | None:
        """Return index of first (presumably only) active bg mode of type mtype."""
        for index in range(len(self.bg_mode_instances)):
            if isinstance(self.bg_mode_instances[index], mtype):
                return index
        return None

    def terminate_bg_mode(self, bg_mode_index: int) -> None:
        """Remove mode from the background mode instance list.
           Remove any associated events from the event queue."""
        mode = self.bg_mode_instances[bg_mode_index]
        del self.bg_mode_instances[bg_mode_index]
        self.event_queue.delete_owned_by(mode)

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
        """Play starting_mode and all subsequent modes."""
        new_mode = starting_mode_index
        while True:
            assert new_mode is not None
            mode = self.modes[new_mode]
            if new_mode in self.bg_mode_instances:
                print(f"Using existing {mode.name} instance.")
                mode_instance = self.bg_mode_instances[new_mode]
            else:
                mode_instance = mode.mode_class(
                    player=self, 
                    name=mode.name, 
                    **self.replace_kwarg_values(mode.kwargs),
                )
                if isinstance(mode_instance, BackgroundMode):
                    print(f"Creating {mode.name} instance.")
                    self.bg_mode_instances[new_mode] = mode_instance
            self.current_mode = new_mode
            print(f"Executing mode {self.current_mode} {mode.name}")
            new_mode = self._play_mode_until_changed(mode_instance)

    def _play_mode_until_changed(self, mode: ModeInterface) -> int | None:
        """Play the specified mode until another mode is selected,
           either by the user or automatically.
           Shut down the system if the (body_back) button is held."""
        new_mode = None
        while new_mode is None:
            try:
                new_mode = mode.execute()
            except ButtonPressed as press:
                button, held = press.args
                if held:
                    raise Shutdown("Button was held.")
                Button.reset()
                assert isinstance(mode, ModeInterface)
                print(f"Button {button} pressed in mode {mode.name}")
                new_mode = mode.button_action(button)
            except ChangeMode as due:
                print("ChangeMode caught")
                new_mode, = due.args
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
        seconds: float | None, 
        elapsed: float = 0.0,
    ) -> None | NoReturn:
        """Wait seconds, after adjusting for
           speed_factor and time already elapsed.
           If seconds is None, wait indefinitely.
           During this time, trigger any events that come due; 
           any button press will terminate waiting."""
        print(f"Wait {seconds}, {elapsed}")
        start = time.time()
        if seconds is not None:
            seconds *= self.speed_factor
        while True:
            now = time.time()
            if seconds is not None:
                remaining = start + seconds - elapsed - now
                end = now + remaining
                if now > end:
                    print(f"break {now} > {end}")
                    break
            if self.event_queue:
                event = self.event_queue.peek()
                if event.due < now:
                    print(f"Running {event}")
                    self.event_queue.pop()
                    event.action()
                elif seconds is None or event.due < end:
                    print(f"Waiting for {event} or button push")
                    duration = event.due - now
                else:
                    print(f"Waiting for remaining {remaining} or button push; queue not empty")
                    duration = remaining
            else:
                if seconds is None:
                    print(f"Waiting for button push")
                    duration = None
                else:
                    print(f"Waiting for remaining {remaining} or button push; queue empty")
                    duration = remaining
            Button.wait(duration)

