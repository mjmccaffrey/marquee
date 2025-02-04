"""Marquee Lighted Sign Project - dimmers"""

import asyncio
from dataclasses import dataclass
import requests
import time
from types import SimpleNamespace

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
    _dimmers = []

    def __init__(self, ip_address, id):
        """Create the dimmer instance."""
        print(time.time())
        self._dimmers.append(self)
        self.ip_address = ip_address
        self.id = id
        self.session = requests.Session()
        # self._get_state() !!!
        self.set(level=100, transition=0.5, output=True)

    def close(self):
        """Clean up."""

    def interpret_set_parameters(self, 
        level: float = None, 
        offset: float = None,
        transition: float = None, 
        output: bool = None,
    ):
        """ """
        if level is not None:
            brightness = level 
        elif offset is not None:
            brightness = self.brightness + offset
        else:
            brightness = None
        params = (
            ({'id': self.id}) |
            ({'brightness': brightness} 
                if brightness is not None else {}) |
            ({'transition_duration': 
                transition or self.transition_default}) |
            ({'on': str(output).lower()} if output is not None else {})
        )
        return SimpleNamespace(
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
        command = self.interpret_set_parameters(
            level=level,
            offset=offset,
            transition=transition,
            output=output,
        )
        print(command)
        try:
            print(
                self.session.get(
                url=command.url,
                params=command.params,
                timeout=1.0,
            )
            )
        except requests.exceptions.ConnectTimeout:
            print(time.time(), self.ip_address, self.id)
        if wait:
            print("WAIT")
            time.sleep(transition)

    @classmethod
    async def _execute_single_command(cls, command):
        """"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=command.url,
                params=command.params,
            ) as response:
                response = await response.text()
            if b := command.params.get('brightness') is not None:
                command.dimmer.brightness = b
    
    @classmethod
    async def execute_multiple_commands(cls, commands):
        """"""
        async with asyncio.TaskGroup() as tg:
            for command in commands:
                tg.create_task(cls._execute_single_command(command))

    @classmethod
    def calibrate(cls):
        """"""
        for id in range(2):
            commands = [
                SimpleNamespace(
                    dimmer=dimmer,
                    url=f'http://{dimmer.ip_address}/rpc/Light.Calibrate',
                    params={'id':id},
                )
                for dimmer in cls._dimmers
            ]
            asyncio.run(cls.execute_multiple_commands(commands))
            print(f"Calibrate running for id: {id}")
            time.sleep(150)
        import sys  # !!! HACK
        sys.exit()  # !!! HACK
