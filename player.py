"""Marquee Lighted Sign Project - player"""

from dataclasses import dataclass, field
from itertools import count
import logging
import signal
import threading
from typing import Any, assert_never, cast, NoReturn
from typing_extensions import override

from api import API
from devices.button import Button
from devices.deviceset import DeviceSet
from schemas import (
    Interrupt, ChangeModeInterrupt, CommandInterrupt, Exit,
    ControlAction, ControlInterrupt, ControlName,
    BaseModeInterface, ModeDefinition,
)
from event import EventSystem
from modes.abstract.mode import Mode
from task import Task, TaskSchedule

log = logging.getLogger('marquee.' + __name__)

@dataclass
class Player:
    """"""
    devices: DeviceSet
    mode_ids: dict[str, int]
    modes: dict[int, ModeDefinition]
    speed_factor: float
    events: EventSystem = field(init=False)
    tasks: TaskSchedule = field(init=False)
    api: API = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        log.info("Initializing player")
        self.active_modes: dict[int, BaseModeInterface] = {}
        self.interrupt: Interrupt | None
        self.interrupt_trigger: threading.Event
        self._reset_interrupt()
        signal.signal(signal.SIGTERM, self._sigterm_received)
        self.events = EventSystem()
        self.tasks = TaskSchedule()
        self.api = API(self)
        self._mode_serial = count()
        self._set_controls_callback()

    def _set_controls_callback(self) -> None:
        """"""
        for name, device in self.devices.items():
            if isinstance(device, Button):
                print(name)
                device.execute_interrupt = self.execute_interrupt

    @override
    def __repr__(self) -> str:
        return f"<{self}>"
    
    @override
    def __str__(self) -> str:
        return "Player"

    def close(self) -> None:
        """Clean up."""
        print("Stopping server...")
        self.api.close()
        print("Server stopped.")
        log.info(f"Player closed.")

    def create_active_mode(
        self, 
        mode_index: int | None = None,
        mode_definition: ModeDefinition | None = None,
        parent: BaseModeInterface | None = None,
    ) -> Mode:
        """Return a new mode instance.
           Does not update self.active_modes."""
        assert (mode_index is None) ^ (mode_definition is None)
        definition = mode_definition or self.modes[cast(int, mode_index)]
        _kwargs: dict[str, Any] = dict(
            index=definition.index,
            name=definition.name, 
            serial=next(self._mode_serial),
            player=self,
            parent=parent,
            devices=self.devices,
            speed_factor=self.speed_factor,
            ) | definition.kwargs
        return definition.cls(**_kwargs)  # type: ignore

    def delete_active_mode(self, mode_index: int) -> None:
        """Delete the instance of mode_index, along
           with any mode instances with instance as parent."""
        mode = self.active_modes[mode_index]
        # Delete children of specified.
        for instance in self.active_modes.values():
            if instance.parent == mode:
                self.delete_active_mode(instance.index)
        # Delete specified.
        print(f'Deleting mode {mode.name} with parent {mode.parent}')
        mode.close()
        del self.active_modes[mode_index]
        self.tasks.delete_owned_by(mode)

    def execute(self, starting_mode_index: int) -> bool:
        """Main event loop.  Return whether to shut down 
           the system, or to just exit."""
        self._effect_new_mode(starting_mode_index)
        try:
            while True:
                try:
                    if self.interrupt_trigger.is_set():
                        assert self.interrupt is not None
                        raise self.interrupt
                    what = self.tasks.next_task_or_wait_duration()
                    if isinstance(what, Task):
                        what.action()
                    else:
                        self.wait(what)
                except Interrupt as it:
                    self._handle_interrupt(it)
        except Exit as ex:
            return ex.shutdown
        assert_never()

    def execute_interrupt(self, interrupt: Interrupt) -> None:
        """"""
        print()
        print("Execute interrupt thread ID", threading.get_ident())
        print(f"{interrupt=}")
        print()
        self.interrupt = interrupt
        if self.interrupt_trigger.is_set():
            raise RuntimeError("TRIGGER IS ALREADY SET!")
        self.interrupt_trigger.set()

    def wait(self, seconds: float | None) -> None | NoReturn:
        """"""
        if self._interrupt_trigger_wait(seconds):
            assert self.interrupt is not None
            raise self.interrupt
        else:
            return None
        
    def _interrupt_trigger_wait(self, seconds: float | None) -> bool:
        """Allows Ctrl-C to interrupt indefinite w"""
        if seconds is not None:
            return self.interrupt_trigger.wait(seconds)
        try:
            while True:
                if self.interrupt_trigger.wait(0.1):
                    break
        except KeyboardInterrupt:
            raise
        else:
            return True

    def _effect_new_mode(self, mode_index: int):
        """Create new mode instance, clean up old, etc."""
        # Create new mode instance
        new_mode = self.create_active_mode(mode_index)
        if new_mode.background:
            # If bg mode of same type already present, delete it.
            if new_mode.index in self.active_modes:
                self.delete_active_mode(new_mode.index)
        else:
            # If any fg mode already present, delete it.
            modes = self.active_modes.values()
            fg_mode = next((m for m in modes if not m.background), None)
            if fg_mode is not None:
                self.delete_active_mode(fg_mode.index)
        self.active_modes[new_mode.index] = new_mode
        print(f'Effected new active mode {new_mode.name.upper()}')
        new_mode.execute()

    def _handle_interrupt(self, it: Interrupt) -> None:
        """"""
        print("Handling Interrupt: ", it)
        match it:
            case CommandInterrupt():
                self._send_api_command(it)
            case ChangeModeInterrupt():
                self._effect_new_mode(it.mode_index)
            case ControlInterrupt():
                # with suppress(ControlInterrupt):
                if it.action == ControlAction.BUTTON_HELD:
                    raise Exit(shutdown=True)
                self._send_control_action(it.control)
            case _:
                raise ValueError(it)
        self._reset_interrupt()

    def _reset_interrupt(self):
        """Prepare for another interrupt."""
        print("Reset interrupt thread ID", threading.get_ident())
        self.interrupt = None
        self.interrupt_trigger = threading.Event()

    def _modes_in_send_order(self) -> list[BaseModeInterface]:
        """Return background mode instances in creation order,
           followed by foreground mode instance if it exists."""
        print(f"{len(self.active_modes)=}")
        return sorted(
            self.active_modes.values(), key=lambda m: not m.background,
        )

    def _send_api_command(self, it: CommandInterrupt) -> None:
        """Execute command on mode instances in send order,
           stopping if one returns True, presumably
           meaning that they handled the command."""
        for mode in self._modes_in_send_order():
            print(f"Sending API command to {mode.name}")
            if mode.command_action(it.command):
                print("Received True; stopping sending.")
                break

    def _send_control_action(self, control: ControlName) -> None:
        """Notify mode instances of control action in send order,
           stopping if one returns True, presumably
           meaning that they handled the control action."""
        for mode in self._modes_in_send_order():
            print(f"Sending control action to {mode.name}")
            if mode.control_action(control):
                print("Received True; stopping sending.")
                break

    def _sigterm_received(self, signal_number, stack_frame) -> None:
        """Callback for SIGTERM received."""
        log.info(f"SIGTERM signal received.")
        raise Exit(shutdown=False)

