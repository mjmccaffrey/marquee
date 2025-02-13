"""Marquee Lighted Sign Project - dimmers"""

import asyncio
from dataclasses import dataclass
import requests
import time

# import aiohttp - Delayed

TRANSITION_MINIMUM = 0.5
TRANSITION_MAXIMUM = 10800.0

class Dimmer:
    """Supports the Shelly Pro Dimmer 2PM."""
    channel_count = 2
    transition_default = 0.5
    _dimmers = []

    @staticmethod
    def finish_setup():
        """"""
        global aiohttp
        import aiohttp

    def __init__(self, ip_address: str):
        """Create the dimmer instance."""
        self._dimmers.append(self)
        self.ip_address = ip_address
        self.session = requests.Session()
        self.channels = [
            DimmerChannel(
                dimmer=self,
                id=id, 
                output=status['output'], 
                brightness=status['brightness']
            ) 
            for id, status in self._get_status()
        ]
        for channel in self.channels:
            print(f'{self.ip_address}:{channel.id}:{channel.output}:{channel.brightness}')

    def close(self):
        """Clean up."""

    def _get_status(self):
        """ Fetch status parameters for all channels. """
        result = self.session.get(
            url=f'http://{self.ip_address}/rpc/Shelly.GetStatus',
            timeout=1.0,
        )
        # !!! Check for result != 200
        # except requests.exceptions.Timeout:
        #     print(time.time(), self.ip_address, self.id)
        json = result.json()
        return [
            (id, json[f'light:{id}'])
            for id in range(self.channel_count)
        ]      
    
    @classmethod
    async def _execute_single_command(cls, command: "DimmerCommand"):
        """ Send individual command as part of asynchonous batch. """
        async with aiohttp.ClientSession() as session: # type: ignore
            async with session.get(
                url=command.url,
                params=command.params,
            ) as response:
                response = await response.text()
                # !!! catch timeout, check for != 200
            if b := command.params.get('brightness') is not None:
                command.channel.brightness = b
    
    @classmethod
    async def execute_multiple_commands(cls, commands: list["DimmerCommand"]):
        """ Send multiple commands asynchronously. """
        async with asyncio.TaskGroup() as tg:
            for command in commands:
                tg.create_task(cls._execute_single_command(command))

    @classmethod
    def calibrate_all(cls):
        """ Execute calibration on all dimmers on each successive channel. """
        for id in range(cls.channel_count):
            commands = [
                DimmerCommand(
                    channel=dimmer.channels[id], 
                    url=f'http://{dimmer.ip_address}/rpc/Light.Calibrate',
                    params={'id':id},
                )
                for dimmer in cls._dimmers
            ]
            asyncio.run(cls.execute_multiple_commands(commands))
            print(f"Calibrate running for channels: {id}")
            time.sleep(150)

class DimmerChannel:
    """ Models a single dimmer channel (light). """
    def __init__(
            self, 
            dimmer:Dimmer, 
            id: int, 
            output: bool, 
            brightness: int,
        ):
        """Create the dimmer channel instance."""
        self.dimmer = dimmer
        self.id = id
        self.output = output
        self.brightness = brightness

    def interpret_set_parameters(
        self, 
        level: float = None, 
        offset: float = None,
        transition: float = None, 
        output: bool = None,
    ):
        """Produce dimmer API parameters from requested values and state."""
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
                transition or self.dimmer.transition_default}) |
            ({'on': str(output).lower()} if output is not None else {})
        )
        return DimmerCommand(
            channel = self,
            url=f'http://{self.dimmer.ip_address}/rpc/Light.Set',
            params=params,
        )

    def set(self, 
            level: float = None, 
            offset: float = None,
            transition: float = None, 
            output: bool = None,
            wait: bool = False,
    ):
        """Set the dimmer channel per requested values and state."""
        command = self.interpret_set_parameters(
            level=level,
            offset=offset,
            transition=transition,
            output=output,
        )
        try:
            self.dimmer.session.get(
                url=command.url,
                params=command.params,
                timeout=1.0,
            )
            # !!! Check for result != 200
        except requests.exceptions.Timeout as e:
            print(time.time(), self.dimmer.ip_address, id, e)
        if wait:
            print("WAIT")
            time.sleep(transition)

@dataclass
class DimmerCommand:
    """ Parameters for giving command to dimmer. """
    channel: DimmerChannel
    url: str
    params: dict
    
@dataclass
class RelayOverride:
    """ Parameters for using dimmers rather than relays. """
    concurrent: bool = False
    level_on: int = 100
    level_off: int = 0
    pace_factor: float = 1.0
    transition_on: float = TRANSITION_MINIMUM
    transition_off: float = TRANSITION_MINIMUM
