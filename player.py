"""Marquee Lighted Sign Project - player"""

from contextlib import suppress
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
    Interrupt, ChangeModeInterrupt, 
    APICommand, CommandInterrupt, 
    BaseModeInterface, ControlAction, ControlInterrupt, 
    DeviceName, Exit,
    InterruptSource, ModeDefinition,
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
        self.mode_instances: dict[int, Mode] = {}
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

    def create_mode_instance(
        self, 
        mode_index: int | None = None,
        mode_definition: ModeDefinition | None = None,
        parent: BaseModeInterface | None = None,
    ) -> Mode:
        """Return a new mode instance.
           Does not update self.mode_instances."""
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

    def delete_mode_instance(self, mode_index: int) -> None:
        """Delete the instance of mode_index, along
           with any mode instances with instance as parent."""
        mode = self.mode_instances[mode_index]
        # Delete children of specified.
        for instance in self.mode_instances.values():
            if instance.parent == mode:
                self.delete_mode_instance(instance.index)
        # Delete specified.
        print(f'Deleting mode {mode.name} with parent {mode.parent}')
        mode.close()
        del self.mode_instances[mode_index]
        self.tasks.delete_owned_by(mode)

    def execute(self, starting_mode_index: int) -> bool:
        """Play the specified starting mode and all subsequent modes.
           Return whether to shut down the system, or just exit."""
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
        if self.interrupt_trigger.wait(seconds):
            assert self.interrupt is not None
            raise self.interrupt
        else:
            return None

    def _effect_new_mode(self, mode_index: int):
        """Create new mode instance, clean up old, etc."""
        # print("EFFECTING", mode_index)
        # Create new mode instance
        new_mode = self.create_mode_instance(mode_index)
        if new_mode.background:
            # If bg mode of same type already present, delete it.
            if new_mode.index in self.mode_instances:
                self.delete_mode_instance(new_mode.index)
        else:
            # If any fg mode already present, delete it.
            modes = self.mode_instances.values()
            fg_mode = next((m for m in modes if not m.background), None)
            if fg_mode is not None:
                self.delete_mode_instance(fg_mode.index)
        self.mode_instances[new_mode.index] = new_mode
        print(f'Effected new mode instance {new_mode.name.upper()}')
        new_mode.execute()

    def _handle_interrupt(self, it: Interrupt) -> None:
        """"""
        print("Handling Interrupt: ", it)
        match it:
            case CommandInterrupt():
                self._execute_api_command(it)
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

    def _execute_api_command(self, it: CommandInterrupt) -> None:
        """Execute command in every mode instance."""
        for mode in self.mode_instances.values():
            match it.command:
                case APICommand.NEXT_ENTRY:
                    mode.next_entry()
                case APICommand.PREVIOUS_ENTRY:
                    mode.previous_entry()
                case APICommand.NEXT_MODE:
                    mode.next_mode()
                case APICommand.PREVIOUS_MODE:
                    mode.previous_mode()
                case _:
                    raise ValueError(it)

    def _send_control_action(self, control: DeviceName) -> None:
        """Execute control action in every mode instance."""
        for mode in self.mode_instances.values():
            mode.control_action(control)

    def _sigterm_received(self, signal_number, stack_frame) -> None:
        """Callback for SIGTERM received."""
        log.info(f"SIGTERM signal received.")
        raise Exit(shutdown=False)

