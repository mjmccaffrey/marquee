"""Marquee Lighted Sign Project - player"""

from dataclasses import dataclass, field
from typing import Any, NoReturn

from button import Button, ButtonPressed, Shutdown
from event import PriorityQueue
from modes.basemode import BaseMode
from modes.backgroundmode import BackgroundMode
from modes.foregroundmode import ForegroundMode
from playerinterface import ChangeMode, PlayerInterface
from specialparams import MirrorParams

@dataclass(repr=False)
class Player(PlayerInterface):
    """Executes one mode at a time. Contains the event queue."""
    event_queue: PriorityQueue = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        print("Initializing player")
        self.active_mode: BackgroundMode | ForegroundMode | None = None
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

    def create_mode_instance(
        self, 
        mode_index: int,
        extra_kwargs: dict[str, Any] = {},
        parent: BaseMode | None = None,
    ) -> BackgroundMode | ForegroundMode:
        """"""
        constructor = self.modes[mode_index]
        full_kwargs = (
            self.replace_kwarg_values(constructor.kwargs) | 
            extra_kwargs
        )
        kwargs = dict(
            player=self,
            index=constructor.index,
            name=constructor.name, 
            modes=self.modes,
            mode_ids=self.mode_ids,
            parent=parent,
            kwargs=full_kwargs,
        )
        if constructor.cls == ForegroundMode:
            kwargs |= dict(
                bells=self.bells,
                buttons=self.buttons,
                drums=self.drums,
                lights=self.lights,
                speed_factor=self.speed_factor,
            )
        return constructor.cls(**kwargs)

    def effect_new_active_mode(self, mode_index: int) -> None:
        """"""

        # If there is an active mode, clean it up.
        # Note: After startup, there is always an active mode.
        if self.active_mode:
            self.event_queue.delete_owned_by(self.active_mode)

        # Create new mode instance
        new_mode = self.create_mode_instance(mode_index)
        assert isinstance(new_mode, BackgroundMode | ForegroundMode)

        # Add new instance to history list
        self.active_mode_history.append(mode_index)

        # Note: A background mode will upon instatiation  
        #       be the active mode, for a very short time.
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

