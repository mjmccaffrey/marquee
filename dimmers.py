"""Marquee Lighted Sign Project - dimmers"""

import asyncio
from dataclasses import dataclass
import requests
import time

import aiohttp

TRANSITION_DEFAULT = 0.5
TRANSITION_MINIMUM = 0.5
TRANSITION_MAXIMUM = 10800.0

class Dimmer:
    """Supports the Shelly Pro Dimmer 2PM."""
    channel_count = 2
    _dimmers: list["Dimmer"] = []

    def __init__(self, index: int, ip_address: str):
        """Create the dimmer instance."""
        self._dimmers.append(self)
        self.index = index
        self.ip_address = ip_address
        print(f"Initializing {self}")
        try:
            self.session = requests.Session()
        except requests.Timeout as err:
            print(err)
            raise
        self.channels: list[DimmerChannel] = [
            DimmerChannel(
                dimmer=self,
                index=self.index * 2 + id,
                id=id, 
                output=status['output'], 
                brightness=status['brightness'],
            ) 
            for id, status in self._get_status()
        ]

    def __str__(self):
        """"""
        return f"dimmer {self.index} @ {self.ip_address}"
    
    def __repr__(self):
        """"""
        return f"<{self}>"
    
    def close(self):
        """Clean up."""

    def _get_status(self) -> list[tuple[int, dict]]:
        """ Fetch status parameters for all channels. """
        try:
            result = self.session.get(
                url=f'http://{self.ip_address}/rpc/Shelly.GetStatus',
                timeout=1.0,
            )
        # !!! Check for result != 200
        except requests.Timeout as err:
            print(err)
            raise
        json = result.json()
        return [
            (id, json[f'light:{id}'])
            for id in range(self.channel_count)
        ]      
    
    @classmethod
    async def _execute_single_command(cls, command: "_DimmerCommand") -> aiohttp.ClientResponse:
        """ Send individual command as part of asynchonous batch. """
        try:
            async with aiohttp.ClientSession() as session: # type: ignore
                async with session.get(
                    url=command.url,
                    params=command.params,
                ) as response:
                    response = await response.json()
        except TimeoutError as err:
            # !!! catch timeout, check for != 200
            print(err)
            raise
        else:
            if (b := command.params.get('brightness')) is not None:
                command.channel.brightness = b
        return response
    
    @classmethod
    async def execute_multiple_commands(cls, commands: list["_DimmerCommand"]) -> list[aiohttp.ClientResponse]:
        """ Send multiple commands asynchronously. """
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(cls._execute_single_command(command))
                for command in commands
            ]
        return [task.result() for task in tasks]

    @classmethod
    def calibrate_all(cls):
        """ Execute calibration on all dimmers on each successive channel. """
        print("Calibrating dimmers")
        # Set all lights all the way on.
        for dimmer in cls._dimmers:
            for channel in dimmer.channels:
                channel.set(
                    brightness=100,
                    output=True,
                )
        time.sleep(5)
        for id in range(cls.channel_count):
            print(f"Calibrating channel {id}")
            commands = [
                _DimmerCommand(
                    channel=dimmer.channels[id], 
                    url=f'http://{dimmer.ip_address}/rpc/Light.Calibrate',
                    params={'id':id},
                )
                for dimmer in cls._dimmers
            ]
            asyncio.run(cls.execute_multiple_commands(commands))
            time.sleep(150)
        print("Calibration complete")

    @classmethod
    def configure_all(cls):
        """ """  # !!!
        DIMMER_ADDRESSES = [
            '192.168.51.111',
            '192.168.51.112',
            '192.168.51.113',
            '192.168.51.114',
            '192.168.51.115',
            '192.168.51.116',
        ]
        print("Configuring dimmers")
        commands = [
            _DimmerCommand(
                channel=cls._dimmers[0].channels[0], 
                url=f'http://{ip}/rpc/Shelly.GetConfig',
                params={},
            )
            for ip in DIMMER_ADDRESSES
        ]
        results = asyncio.run(cls.execute_multiple_commands(commands))
        for result in results:
            print()
            print(result)
            print()

class DimmerChannel:
    """ Models a single dimmer channel (light). """
    def __init__(
            self, 
            dimmer: Dimmer, 
            index: int,
            id: int, 
            output: bool, 
            brightness: int,
        ):
        """Create the dimmer channel instance."""
        self.dimmer = dimmer
        self.index = index
        self.ip_address = self.dimmer.ip_address
        self.id = id
        print(f"Initializing {self}")
        self.output = output
        self.brightness = brightness
        self.next_update: float = 0
        self.set(output=True)  # !!! make part of a larger init?

    def __str__(self):
        return (f"dimmer {self.dimmer.index} channel {self.index}")
    
    def __repr__(self):
        return f"<{self}>"
    
    def make_set_command(
        self, 
        brightness: int | None = None, 
        offset: int | None = None,
        transition: float | None = None, 
        output: bool | None = None,
    ) -> "_DimmerCommand":
        """Produce dimmer API parameters from requested values and state."""
        assert transition is None or transition >= TRANSITION_MINIMUM
        if brightness is not None:
            new_brightness = brightness 
        elif offset is not None:
            new_brightness = self.brightness + offset
        else:
            new_brightness = None
        params = (
            ({'id': self.id}) |
            ({'brightness': new_brightness} 
                if new_brightness is not None else {}) |
            ({'transition_duration': 
                transition or TRANSITION_DEFAULT}) |
            ({'on': str(output).lower()} if output is not None else {})
        )
        return _DimmerCommand(
            channel = self,
            url=f'http://{self.ip_address}/rpc/Light.Set',
            params=params,
        )

    def set(self, 
            brightness: int | None = None, 
            offset: int | None = None,
            transition: float | None = None, 
            output: bool | None = None,
            wait: bool = False,
    ):
        """Set the dimmer channel per requested values and state."""
        #print("start:", time.time())
        command = self.make_set_command(
            brightness=brightness,
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
            print(time.time(), self.ip_address, id, e)
        else:
            if (b := command.params.get('brightness')) is not None:
                self.brightness = b
        if wait:
            assert transition is not None
            print("WAIT")
            time.sleep(transition)
        #print("end:", time.time())

@dataclass
class _DimmerCommand:
    """ Parameters for giving command to dimmer. """
    channel: DimmerChannel
    url: str
    params: dict
    
@dataclass
class RelayOverride:
    """ Parameters for using dimmers rather than relays. """
    concurrent: bool = True
    brightness_on: int = 100
    brightness_off: int = 0
    speed_factor: float = 1.0
    transition_on: float | None = None
    transition_off: float | None = None
