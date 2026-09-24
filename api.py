"""Marquee Lighted Sign Project - api"""

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from apiserver import APIServer
from playerresources import PlayerResources
from schemas import (
    ChangeModeInterrupt, ControlAction, ControlInterrupt,
    APICommand, CommandInterrupt, 
    DeviceName, InterruptSource,
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
            app=self.app, host="127.0.0.1", port=8000,
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
        self.app.get("/delete_mode/{mode_id}")(self.delete_mode)
        self.app.get("/active_modes")(self.get_active_modes)
        self.app.get("/mode_ids")(self.get_mode_ids)
        self.app.get("/give_command/{name}")(self.give_command)
        self.app.get("/press_button/{name}")(self.press_button)
        self.app.get("/set_mode/{mode_id}")(self.set_mode)

    #

    def delete_mode(self, mode_id: str) -> JSONResponse:
        """Delete the specified mode instance."""
        mode_index = self._lookup_mode_index(mode_id)
        if mode_index is None:
            return LookupFailure
        self.player.delete_mode_instance(mode_index)
        return Success
        
    def get_active_modes(self) -> dict:
        """Get mode instances."""
        return self.player.mode_instances

    def get_mode_ids(self) -> dict:
        """Get IDs of all mode definitions."""
        return self.player.mode_ids

    def give_command(self, name: str) -> None:
        """Issue the specified command."""
        self.player.execute_interrupt(
            CommandInterrupt(
                source=InterruptSource.API,
                command=APICommand(name),
            )
        )

    def press_button(self, name: DeviceName) -> None:
        """Press the specified button."""
        self.player.execute_interrupt(
            ControlInterrupt(
                action=ControlAction.BUTTON_PRESSED,
                control=name, 
                source=InterruptSource.API,
            )
        )
        self.player.devices[name.value].pressed_via_api()

    def set_mode(self, mode_id: str) -> JSONResponse:
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
        
