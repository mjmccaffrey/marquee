"""Marquee Lighted Sign Project - api"""

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from apiserver import APIServer
from devices import joystick
from playerresources import PlayerResources
from schemas import (
    ButtonName, ControlName, DeviceName,
    ChangeModeInterrupt, ControlAction, ControlInterrupt, 
    APICommand, CommandInterrupt, InterruptSource,
)

log = logging.getLogger('marquee.' + __name__)

LookupFailure = JSONResponse({'status': 'lookup failure'}, status_code=404)
Success = JSONResponse(None)

class API:
    """"""

    def __init__(self, player: PlayerResources) -> None:
        """Initialize."""
        log.info("Initializing API")
        self.player = player
        self._start_api_server()
        self._register_api_routes()

    def _start_api_server(self) -> None:
        """"""
        self.app = FastAPI()
        self.server = APIServer(
            app=self.app, host="0.0.0.0", port=8000,
        )
        self.server.start()
        print("API server started.")

    def _lookup_mode_index(self, mode_id: str) -> int | None:
        """Return index of the mode definition with id."""
        try:
            return self.player.mode_ids[mode_id]
        except LookupError:
            return None

    def close(self) -> None:
        """Clean up."""
        print("Stopping API server...")
        self.server.stop()
        print("Server stopped.")
        log.info(f"API closed.")

    def _register_api_routes(self) -> None:
        """"""
        self.app.delete("/mode/{mode_id}")(self.delete_mode)
        self.app.get("/modes")(self.get_active_modes)
        self.app.get("/mode_definitions")(self.get_mode_definitions)
        self.app.post("/mode/{mode_id}")(self.post_mode)
        #
        self.app.post("/button/{button}")(self.post_button)
        self.app.post("/command/{command}")(self.post_command)
        self.app.post("/joystick/stop")(self.post_joystick_stop)
        self.app.post("/joystick/{direction}")(self.post_joystick)

    # ***** API Methods *****

    def delete_mode(self, mode_id: str) -> JSONResponse:
        """Delete the specified mode instance."""
        mode_index = self._lookup_mode_index(mode_id)
        if mode_index is None:
            return LookupFailure
        self.player.delete_mode_instance(mode_index)
        return Success
        
    def get_active_modes(self) -> dict:
        """Get mode instances."""
        return {
            m.index: 
            f"{m.name}{' (background)' if m.background else ''}"
            for m in self.player.mode_instances.values()
        }

    def get_mode_definitions(self) -> dict:
        """Get IDs of all mode definitions."""
        return {
            m.index:
            f"{m.name}{' (background)' if m.cls.background else ''}"
            for i, m in self.player.modes.items()
        }

    def post_command(self, command: APICommand) -> None:
        """Issue the specified command."""
        self.player.execute_interrupt(
            CommandInterrupt(
                source=InterruptSource.API,
                command=command,
            )
        )

    def post_button(self, button: ButtonName) -> None:
        """Press the specified button."""
        self.player.execute_interrupt(
            ControlInterrupt(
                action=ControlAction.BUTTON_PRESSED,
                control=ControlName("button_" + button), 
                source=InterruptSource.API,
            )
        )

    def post_joystick(self, direction: joystick.Direction) -> None:
        """"""
        print(f"JOYSTICK {direction}")
        assert 'joystick' in self.player.devices
        self.player.devices['joystick'].override = direction

    def post_joystick_stop(self) -> None:
        """"""
        print("JOYSTICK STOP")
        assert 'joystick' in self.player.devices
        self.player.devices['joystick'].override = None

    def post_mode(self, mode_id: str) -> JSONResponse:
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
        
    # def _api_get_lights(self) -> dict:
    #     """"""
    #     # index, channel_enum_name, brightness, color, on

    # def _api_set_brightness_factor(self) -> None:
    #     """"""
        
    # def _api_set_speed_factor(self) -> None:
    #     """"""
        
