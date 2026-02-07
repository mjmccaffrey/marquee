"""Marquee Lighted Sign Project - player"""

from dataclasses import dataclass, field
from typing import Any, NoReturn

from devices.button import Button, ButtonPressed, Shutdown
from devices.devices_misc import ButtonSet
from event import PriorityQueue
from instruments import BellSet, DrumSet
from lightset import ClickSet, LightSet
from modes.backgroundmode import BackgroundMode
from modes.foregroundmode import ForegroundMode
from modes.mode_misc import ChangeMode, ModeDefinition
from specialparams import MirrorParams

@dataclass()
class Player:
    """Executes one mode at a time. Contains the event queue."""
    modes: dict[int, ModeDefinition]
    mode_ids: dict[str, int]
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    top: LightSet
    clicker: ClickSet
    speed_factor: float
    pace: float = field(init=False)
    bg_mode_instances: dict = field(init=False)
    event_queue: PriorityQueue = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        print("Initializing player")
        self.active_mode: BackgroundMode | ForegroundMode | None = None
        self.live_bg_modes: dict[int, BackgroundMode] = {}
        self.event_queue = PriorityQueue()

    def __repr__(self) -> str:
        return f"<{self}>"
    
    def __str__(self) -> str:
        return "Player"

    def close(self) -> None:
        """Clean up."""
        print(f"Player {self} closed.")

    def create_mode_instance(
        self, 
        mode_index: int,
        kwargs: dict[str, Any] = {},
        parent: object | None = None,  # BaseMode
    ) -> BackgroundMode | ForegroundMode:
        """"""
        if mode_index is not None:
            definition = self.modes[mode_index]
            _kwargs = dict(
                index=definition.index,
                name=definition.name, 
                speed_factor=self.speed_factor,
                create_mode_instance=self.create_mode_instance,
                replace_kwarg_values=self.replace_kwarg_values,
                event_queue=self.event_queue,
                modes=self.modes,
                mode_ids=self.mode_ids,
                parent=parent,
            )
            _kwargs |= (
                self.replace_kwarg_values(definition.kwargs) | 
                kwargs
            )
        if issubclass(definition.cls, ForegroundMode):
            _kwargs |= dict(
                bells=self.bells,
                buttons=self.buttons,
                drums=self.drums,
                lights=self.lights,
                top=self.top,
                clicker=self.clicker,
                speed_factor=self.speed_factor,
            )
        return definition.cls(**_kwargs)  # type: ignore

    def effect_new_active_mode(self, mode_index: int) -> BackgroundMode | ForegroundMode:
        """"""

        # If there is an active mode and it is of type ForeGround, 
        # clean it up.
        # Note: After startup, there is always an active mode.
        if isinstance(self.active_mode, ForegroundMode):
            self.event_queue.delete_owned_by(self.active_mode)

        # Create new mode instance
        new_mode = self.create_mode_instance(mode_index)
        assert isinstance(new_mode, BackgroundMode | ForegroundMode)

        # Note: A background mode will upon instatiation  
        #       be the active mode, for a very short time.
        if isinstance(new_mode, BackgroundMode):
            # If bg mode of same type already present, clean it up.
            if (conflict := self.live_bg_modes.pop(new_mode.index, None)):
                self.event_queue.delete_owned_by(conflict)
            # Add new bg mode to bg mode list
            self.live_bg_modes[new_mode.index] = new_mode

        # Return new mode instance
        return new_mode

    def execute(self, starting_mode_index: int) -> None:
        """Play the specified starting mode and all subsequent modes."""
        new_mode_index: int | None = starting_mode_index
        while True:
            try:
                if new_mode_index is not None:
                    self.active_mode = self.effect_new_active_mode(new_mode_index)
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
                # print("ChangeMode caught")
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
        vars: dict[str, Any] = {
            'LIGHT_PATTERN': self.lights.relay_pattern,
        }
        if self.active_mode is not None:
            vars['PREVIOUS_MODE'] = self.active_mode.index
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

