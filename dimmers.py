"""Marquee Lighted Sign Project - dimmers"""

import asyncio
from dataclasses import dataclass
import requests
import time
import types

import aiohttp

TRANSITION_MINIMUM = 0.5
TRANSITION_MAXIMUM = 10800.0

@dataclass
class RelayOverride:
    """"""
    concurrent: bool = False
    level_on: int = 100
    level_off: int = 0
    transition_on: float = TRANSITION_MINIMUM
    transition_off: float = TRANSITION_MINIMUM

class Dimmer:
    """Supports the Shelly Pro Dimmer 2PM."""

    transition_default = 0.5

    def __init__(self, ip_address, id):
        """Create the dimmer instance."""
        print(time.time())
        self.ip_address = ip_address
        self.id = id
        # self._get_state() !!!
        self.session = requests.Session()
        self.set(level=100, output=True)

    def close(self):
        """Clean up."""

    def _interpret_parameters(self, 
        level: float = None, 
        offset: float = None,
        transition: float = None, 
        output: bool = None,
    ):
        """ """
        if level:
            brightness = level 
        elif offset:
            brightness = self.brightness + offset
        else:
            brightness = None
        params = (
            ({'id': self.id}) |
            ({'brightness': brightness} 
                if brightness is not None else {}) |
            ({'transition_duration': 
                transition or self.transition_default}) |
            ({'on': output} if output is not None else {})
        )
        return types.SimpleNamespace(
            dimmer=self,
            url=f'http://{self.ip_address}/rpc/Light.Set',
            params=params,
        )

    def set(self, 
            level: float = None, 
            offset: float = None,
            transition: float = None, 
            output: bool = None,
            wait: bool = False,
    ):
        """ """
        command = self._interpret_parameters(
            level=level,
            offset=offset,
            transition=transition,
            output=output,
        )
        try:
            self.session.get(
                url=command.url,
                params=command.params,
                timeout=1.0,
            )
        except requests.exceptions.ConnectTimeout:
            print(time.time(), self.ip_address, self.id)
        if wait:
            print("WAIT")
            time.sleep(self.transition_default)

    @classmethod
    async def _execute_single_command(cls, command):
        """"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=command.url,
                params=command.params,
            ) as response:
                response = await response.text()
            if b := command.params['brightness'] is not None:
                command.dimmer.brightness = b
    
    @classmethod
    async def execute_multiple_commands(cls, commands):
        """"""
        async with asyncio.TaskGroup() as tg:
            for command in commands:
                tg.create_task(cls._execute_single_command(command))
