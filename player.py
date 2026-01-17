"""Marquee Lighted Sign Project - player"""

from dataclasses import dataclass, field
from typing import Any, NoReturn

from button import Button, ButtonPressed, Shutdown
from event import PriorityQueue
from modes.backgroundmode import BackgroundMode
from modes.foregroundmode import ForegroundMode
from modes.modeinterface import ModeInterface
from playerinterface import PlayerInterface
from specialparams import MirrorParams

type ModeInstance = BackgroundMode | ForegroundMode

class ChangeMode(Exception):
    """Change mode exception."""

@dataclass(repr=False)
class Player(PlayerInterface):
    """Executes one mode at a time. Contains the event queue."""
    event_queue: PriorityQueue = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        print("Initializing player")
        self.active_mode: ModeInstance | None = None
        self.active_mode_history: list[int] = []
        self.live_bg_modes: dict[int, BackgroundMode] = {}
        self.event_queue = PriorityQueue()
        MirrorParams.mirror = self.drums.mirror

    def __repr__(self) -> str:
        return "Player repr"
    
    def __str__(self) -> str:
        return "Player str"
    
    def close(self) -> None:
        """Clean up."""
        print(f"Player {self} closed.")

    def change_mode(self, mode_index: int) -> NoReturn:
        """Effects changing active mode to mode_index."""
        print(f"Changing to mode {mode_index}")
        raise ChangeMode(mode_index)



    def effect_new_active_mode(self, mode_index: int) -> None:
        """"""

        # If there is an active mode, clean it up.
        # Note: After startup, there is always an active_mode.
        if self.active_mode:
            self.event_queue.delete_owned_by(self.active_mode)

        # Create new mode instance
        constructor = self.modes[mode_index]
        new_mode = constructor.cls(
            player=self,
            index=constructor.index,
            name=constructor.name, 
            **self.replace_kwarg_values(constructor.kwargs),
        )

        # Add new instance to history list
        self.active_mode_history.append(new_mode)

        # If new mode is of type background...
        # Note: A background mode will also be 
        #       the active mode for a very short time.
        if isinstance(new_mode, BackgroundMode):
            # If bg mode of same type already present, clean it up.
            
            if (conflict := self.live_bg_modes.pop(new_mode.index, None)):
                self.event_queue.delete_owned_by(conflict)
            # Add new bg mode to bg mode list
            self.live_bg_modes[new_mode.index] = new_mode

        self.active_mode = new_mode



    def execute(self, starting_mode_index: int) -> None:
        """Play the specified starting mode and all subsequent modes."""
        new_mode_index: int | None = starting_mode_index
        while True:
            try:
                if new_mode_index is not None:
                    self.effect_new_active_mode(new_mode_index)
                    new_mode_index = None
                assert self.active_mode is not None
                print(f"Executing mode {self.active_mode}")
                self.active_mode.execute()
                self.wait()
            except ButtonPressed as press:
                button, held = press.args
                if held:
                    raise Shutdown("Button was held.")
                Button.reset()
                assert self.active_mode is not None
                print(f"Button {button} pressed in mode {self.active_mode}")
                new_mode_index = self.notify_button_action(button)
            except ChangeMode as cm:
                print("ChangeMode caught")
                new_mode_index, = cm.args

    def notify_button_action(self, button: Button) -> int | None:
        """Notify all background modes, and active mode, 
           of button action. Return active mode's response."""
        for mode in self.live_bg_modes.values():
            mode.button_action(button)
        assert self.active_mode is not None
        return self.active_mode.button_action(button)

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

    def wait(
        self, 
        seconds: float | None = None, 
    ) -> None | NoReturn:
        """Wait seconds, adjusted for speed_factor.
           If seconds is None, wait indefinitely (in this case,
           the current mode instance will never be returned to).
           While waiting, trigger any events that come due; 
           any button press will terminate waiting."""

        if seconds is not None:
            seconds *= self.speed_factor
        self.event_queue.wait(seconds, Button.wait)

