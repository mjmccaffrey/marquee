"""Marquee Lighted Sign Project - dimmers"""

from abc import ABC
import asyncio
from dataclasses import dataclass
from typing import ClassVar, Protocol

import aiohttp
import requests

TRANSITION_DEFAULT = 0.5
TRANSITION_MINIMUM = 0.5
TRANSITION_MAXIMUM = 10800.0


class DimmerModule(Protocol):
    """Protocol for any dimmer module."""
    
    channel_count: ClassVar[int]

    def close(self) -> None:
        """Clean up."""
        ...

    @staticmethod
    async def execute_multiple_commands(
        commands: list["_DimmerCommand"]
    ) -> list[aiohttp.ClientResponse]:
        """Send multiple commands asynchronously."""
        ...


class ShellyDimmer(DimmerModule, ABC):
    """Supports Shelly Dimmers."""

    channel_count: ClassVar[int]

    def __init__(self, index: int, ip_address: str) -> None:
        """Create the dimmer instance."""
        self.index = index
        self.ip_address = ip_address
        print(f"Initializing {self}")
        self.session = requests.Session()
        try:
            self.channels: list[DimmerChannel] = [
                DimmerChannel(
                    dimmer=self,
                    index=self.index * 2 + id,
                    id=id, 
                    brightness=status['brightness'],
                ) 
                for id, status in self._get_status()
            ]
        except requests.exceptions.Timeout as e:
            print(f"*** Failed to reach '{self.ip_address}' ***")
            print(f"*** Error: {e} ***")
            raise OSError from None

    def __init_subclass__(cls, channel_count: int) -> None:
        """"""
        cls.channel_count = channel_count

    def __str__(self) -> str:
        return f"{type(self).__name__} {self.index} @ {self.ip_address}"
    
    def __repr__(self) -> str:
        return f"<{self}>"
    
    def close(self) -> None:
        """Clean up."""
        print(f"Dimmer {self} closed.")

    def _get_status(self) -> list[tuple[int, dict]]:
        """ Fetch status parameters for all channels. """
        result = self.session.get(
            url=f'http://{self.ip_address}/rpc/Shelly.GetStatus',
            timeout=1.0,
        )
        json = result.json()
        return [
            (id, json[f'light:{id}'])
            for id in range(self.channel_count)
        ]      
    
    @staticmethod
    async def _execute_single_command(command: "_DimmerCommand") -> aiohttp.ClientResponse:
        """ Send individual command as part of asynchonous batch. """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=command.url,
                params=command.params,
                raise_for_status=True,
            ) as response:
                response = await response.json()
        if (b := command.params.get('brightness')) is not None:
            command.channel.brightness = b
        return response
    
    @staticmethod
    async def execute_multiple_commands(
        commands: list["_DimmerCommand"]
    ) -> list[aiohttp.ClientResponse]:
        """Send multiple commands asynchronously."""
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    ShellyDimmer._execute_single_command(command)
                )
                for command in commands
            ]
        return [task.result() for task in tasks]


class DimmerChannel:
    """ Models a single dimmer channel (light). """
    def __init__(
            self, 
            dimmer: ShellyDimmer, 
            index: int,
            id: int, 
            brightness: int,
        ) -> None:
        """Create the dimmer channel instance."""
        self.dimmer = dimmer
        self.index = index
        self.ip_address = self.dimmer.ip_address
        self.id = id
        self.brightness = brightness
        self.next_update: float = 0
        self.set()  # Ensure on==true
            
    def __str__(self) -> str:
        return (f"dimmer {self.dimmer.index} channel {self.index}")
    
    def __repr__(self) -> str:
        return f"<{self}>"
    
    def calibrate(self) -> None:
        """Initiate dimmer channel calibration."""
        command = _DimmerCommand(
            channel = self,
            url=f'http://{self.ip_address}/rpc/Light.Calibrate',
            params={'id':self.id},
        )
        response = self.dimmer.session.get(
            url=command.url,
            params=command.params,
            timeout=1.0,
        )
        response.raise_for_status()

    def make_set_command(
        self, 
        brightness: int | None = None, 
        offset: int | None = None,
        transition: float | None = None, 
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
            ({'on': 'true'})
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
    ) -> None:
        """Set the dimmer channel per requested values and state."""
        command = self.make_set_command(
            brightness=brightness,
            offset=offset,
            transition=transition,
        )
        print(f"{command=}")
        response = self.dimmer.session.get(
            url=command.url,
            params=command.params,
            timeout=1.0,
        )
        response.raise_for_status()
        if (b := command.params.get('brightness')) is not None:
            self.brightness = b


class ShellyProDimmer2PM(ShellyDimmer, channel_count=2):
    """Supports the Shelly Pro Dimmer 2PM."""


@dataclass
class _DimmerCommand:
    """ Parameters for giving command to dimmer. """
    channel: 'DimmerChannel'
    url: str
    params: dict

