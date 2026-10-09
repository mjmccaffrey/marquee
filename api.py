"""Marquee Lighted Sign Project - api"""

from enum import IntEnum, StrEnum
import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from apiserver import APIServer
from devices import joystick
from playerresources import PlayerResources
from schemas import (
    ButtonName, ControlName,
    ChangeModeInterrupt, ControlAction, ControlInterrupt, 
    APICommand, CommandInterrupt, InterruptSource,
    ModeDefinition,
)

log = logging.getLogger('marquee.' + __name__)

LookupFailure = JSONResponse({'status': 'lookup failure'}, status_code=404)
Success = JSONResponse(None)


class Tag(StrEnum):
    MODES = "Modes"
    INPUTS = "Inputs"
    OUTPUTS = "Outputs"
    COMMANDS = "Commands"


class API:
    """"""

    def __init__(self, player: PlayerResources) -> None:
        """Initialize."""
        log.info("Initializing API")
        self.player = player
        self._build_mode_def_enum()
        self._start_api_server()
        self._register_api_routes()

    def _build_mode_def_enum(self) -> None:
        """"""
        if TYPE_CHECKING:
            class ModeDefEnum(IntEnum):
                ONE = 1
        else:
            ModeDefEnum = IntEnum(
                "ModeDefEnum", [
                    (self._mode_description(m), m.index)
                    for m in self.player.modes.values()
                ]
            )

    def _start_api_server(self) -> None:
        """"""
        self.app = FastAPI()
        self.server = APIServer(
            app=self.app, host="0.0.0.0", port=8000,
        )
        self.server.start()
        print("API server started.")

    def close(self) -> None:
        """Clean up."""
        print("Stopping API server...")
        self.server.stop()
        print("Server stopped.")
        log.info(f"API closed.")

    def _lookup_mode_index(self, mode_id: str) -> int | None:
        """Return index of the mode definition with id."""
        try:
            return self.player.mode_ids[mode_id]
        except LookupError:
            return None

    @staticmethod
    def _mode_description(mode: ModeDefinition) -> str:
        """"""
        return (
            f"{mode.index} {mode.name}"
            f"{' (background)' if mode.cls.background else ''}"
        )
    
    def _register_api_routes(self) -> None:
        """"""
        # Modes
        self.app.post("/mode/{mode_id}", tags=[Tag.MODES]) \
                     (self.create_active_mode)
        self.app.get("/modes", tags=[Tag.MODES]) \
                    (self.get_active_modes)
        self.app.get("/mode_definitions", tags=[Tag.MODES]) \
                    (self.get_mode_definitions)
        self.app.delete("/mode/{mode_id}", tags=[Tag.MODES]) \
                       (self.delete_active_mode)
        # Inputs
        self.app.post("/button/{button}", tags=[Tag.INPUTS]) \
                     (self.press_button)
        self.app.post("/joystick/stop", tags=[Tag.INPUTS]) \
                     (self.stop_overriding_joystick)
        self.app.post("/joystick/{direction}", tags=[Tag.INPUTS]) \
                     (self.override_joystick)
        # Outputs
        self.app.post("/brightness/{factor}", tags=[Tag.OUTPUTS]) \
                     (self.set_brightness)
        # Commands
        self.app.post("/command/{command}", tags=[Tag.COMMANDS]) \
                     (self.issue_command)


    # ***** Modes *****

    def create_active_mode(self, mode_id: str) -> JSONResponse:
        """Create new instance of specified mode definition.
           If an instance of that definition already exists, delete it."""
        mode_index = self._lookup_mode_index(mode_id)
        if mode_index is None:
            return LookupFailure
        self.player.execute_interrupt(
            ChangeModeInterrupt(
                source=InterruptSource.API,
                mode_index=mode_index,
            )
        )
        return Success
        
    def get_active_modes(self) -> list[str]:
        """Get mode instances."""
        return [
            self._mode_description(self.player.modes[index])
            for index in self.player.active_modes
        ]

    def get_mode_definitions(self) -> list[str]:
        """Get mode definitions."""
        return [
            self._mode_description(m)
            for m in self.player.modes.values()
        ]

    def delete_active_mode(self, mode_id: str) -> JSONResponse:
        """Delete the specified mode instance."""
        mode_index = self._lookup_mode_index(mode_id)
        if mode_index is None:
            return LookupFailure
        self.player.delete_active_mode(mode_index)
        return Success
       

    # ***** Inputs *****

    def press_button(self, button: ButtonName) -> None:
        """Press the specified button."""
        self.player.execute_interrupt(
            ControlInterrupt(
                action=ControlAction.BUTTON_PRESSED,
                control=ControlName("button_" + button), 
                source=InterruptSource.API,
            )
        )

    def stop_overriding_joystick(self) -> None:
        """"""
        print("JOYSTICK STOP")
        assert 'joystick' in self.player.devices
        self.player.devices['joystick'].override = None

    def override_joystick(self, direction: joystick.Direction) -> None:
        """"""
        print(f"JOYSTICK {direction}")
        assert 'joystick' in self.player.devices
        self.player.devices['joystick'].override = direction
        print(f"Joystick: {direction}")


    # ***** Outputs *****

    def set_brightness(self, factor: float) -> None:
        """"""
        self.player.devices['lights'].change_brightness_factor(factor)


    # ***** Commands *****

    def issue_command(self, command: APICommand) -> None:
        """Issue the specified command."""
        self.player.execute_interrupt(
            CommandInterrupt(
                source=InterruptSource.API,
                command=command,
            )
        )


