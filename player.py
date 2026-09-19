"""Marquee Lighted Sign Project - player"""

from contextlib import suppress
from dataclasses import dataclass, field
from itertools import count
import logging
import signal
import threading
from typing import Any, assert_never, cast, NoReturn
from typing_extensions import override

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from apiserver import APIServer
from devices.button import Button
from devices.deviceset import DeviceSet
from schemas import (
    Interrupt, ChangeModeInterrupt, 
    APICommand, CommandInterrupt, 
    ControlAction, ControlInterrupt, 
    DeviceName, Exit,
    InterruptSource, ModeDefinition,
)
from event import EventSystem
from modes.abstract.mode import Mode
from task import TaskSchedule

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
    api: FastAPI = field(init=False)
    api_server: APIServer = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        log.info("Initializing player")
        self.mode_instances: dict[int, Mode] = {}
        self.mode_serial = count()
        self.interrupt: Interrupt | None
        self.interrupt_trigger: threading.Event
        self.reset_interrupt()
        signal.signal(signal.SIGTERM, self._sigterm_received)
        self.events = EventSystem()
        self.tasks = TaskSchedule()
        self._start_api_server()
        self._register_api_routes()
        self._set_controls_callback()

    def _start_api_server(self) -> None:
        """"""
        self.api = FastAPI()
        self.api_server = APIServer(app=self.api, host="127.0.0.1", port=8000)
        self.api_server.start()
        print("API server started.")

    def _register_api_routes(self) -> None:
        """"""
        self.api.get("/mode_ids")(self._api_get_mode_ids)
        self.api.get("/press_button/{name}")(self._api_press_button)
        self.api.get("/give_command/{name}")(self._api_give_command)
        self.api.get("/set_mode/{mode_id}")(self._api_set_mode)

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
        self.api_server.stop()
        print("Server stopped.")
        log.info(f"Player closed.")

    def create_mode_instance(
        self, 
        mode_index: int | None = None,
        mode_definition: ModeDefinition | None = None,
        parent: Mode | None = None,
    ) -> Mode:
        """Return a new mode instance.
           Does not update self.mode_instances."""
        assert (mode_index is None) ^ (mode_definition is None)
        definition = mode_definition or self.modes[cast(int, mode_index)]
        _kwargs: dict[str, Any] = dict(
            index=definition.index,
            name=definition.name, 
            serial=next(self.mode_serial),
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
                log.info('player execute loop top')
                try:
                    self.tasks.wait(wait_fn=self.wait)
                except Interrupt as it:
                    self._handle_interrupt(it)
                    self.reset_interrupt()
        except Exit as ex:
            return ex.shutdown
        assert_never()

    def execute_interrupt(self, interrupt: Interrupt) -> None:
        """"""
        print()
        print("Thread ID", threading.get_ident())
        print(f"{interrupt=}")
        print()
        self.interrupt = interrupt
        self.interrupt_trigger.set()

    def reset_interrupt(self):
        """Prepare for another interrupt."""
        self.interrupt = None
        self.interrupt_trigger = threading.Event()

    def wait(self, seconds: float | None) -> None | NoReturn:
        """"""
        log.info("PLAYER.WAIT")
        if self.interrupt_trigger.wait(seconds):
            assert self.interrupt is not None
            print("RAISING", self.interrupt)
            raise self.interrupt
        else:
            log.info("NOT TRIGGERED")
            return None

    def _effect_new_mode(self, mode_index: int):
        """Create new mode instance, clean up old, etc."""
        print("EFFECTING", mode_index)
        # Create new mode instance
        new_mode = self.create_mode_instance(mode_index)
        if new_mode.background:
            # If bg mode of same type already present, delete it.
            if new_mode.index in self.mode_instances:
                self.delete_mode_instance(new_mode.index)
        else:
            # If any fg mode already present, delete it.
            fg_mode = self._foreground_mode_instance()
            if fg_mode is not None:
                self.delete_mode_instance(fg_mode.index)
        self.mode_instances[new_mode.index] = new_mode
        print(f'Effected new mode instance {new_mode.name.upper()}')
        new_mode.execute()

    def _foreground_mode_instance(self) -> Mode | None:
        """"""
        fg_iter = (m for m in self.mode_instances.values() if not m.background)
        return next(fg_iter, None)

    def _handle_interrupt(self, it: Interrupt) -> None | NoReturn:
        """"""
        print("handling: ", it)
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

    def _api_get_mode_ids(self) -> dict:
        """"""
        return self.mode_ids

    # def _api_get_lights(self) -> dict:
    #     """"""
    #     # index, channel_enum_name, brightness, color, on

    def _api_set_mode(self, mode_id: str) -> JSONResponse:
        """"""
        try:
            mode_index = self.mode_ids[mode_id]
        except LookupError:
            return JSONResponse({'status': 'lookup failure'}, status_code=404)
        else:
            self.execute_interrupt(
                ChangeModeInterrupt(
                    source=InterruptSource.API,
                    mode_index=mode_index,
                )
            )
            return JSONResponse(None)
        
    # def _api_set_brightness_factor(self) -> None:
    #     """"""
        
    # def _api_set_speed_factor(self) -> None:
    #     """"""
        
    def _api_press_button(self, name: DeviceName) -> None:
        """"""
        self.devices[name.value].pressed_via_api()

    def _api_give_command(self, name: str) -> None:
        """"""
        self.execute_interrupt(
            CommandInterrupt(
                source=InterruptSource.API,
                command=APICommand(name),
            )
        )

    def _execute_api_command(self, it: CommandInterrupt) -> None:
        """"""
        fg_mode = self._foreground_mode_instance()
        if fg_mode is None:
            return
        match it.command:
            case APICommand.NEXT_ENTRY:
                fg_mode.next_entry()
            case APICommand.PREVIOUS_ENTRY:
                fg_mode.previous_entry()
            case APICommand.NEXT_MODE:
                fg_mode.next_mode()
            case APICommand.PREVIOUS_MODE:
                fg_mode.previous_mode()
            case _:
                raise ValueError(it)

    def _send_control_action(self, control: DeviceName) -> None:
        """Notify all background modes, and active mode, 
           of control action."""
        for mode in self.mode_instances.values():
            if mode.background:
                mode.control_action(control)
        fg_mode = self._foreground_mode_instance()
        if fg_mode is not None:
            fg_mode.control_action(control)

    def _sigterm_received(self, signal_number, stack_frame) -> None:
        """Callback for SIGTERM received."""
        log.info(f"SIGTERM signal received.")
        raise Exit(shutdown=False)

