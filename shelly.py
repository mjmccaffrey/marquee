"""Marquee Lighted Sign Project - shelly"""

from abc import ABC
import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

import aiohttp
import requests

from bulb import Bulb, DimBulb
from lightcontroller import (
    ChannelUpdate, _ChannelCommand, Color,
    LightController, LightChannel,
)

@dataclass
class ShellyController(LightController, bulb_compatibility=DimBulb):
    """Virtual consolidated controller."""

    trans_def: ClassVar[float] = 0.5
    trans_min: ClassVar[float] = 0.5
    trans_max: ClassVar[float] = 10800.0

    dimmers: Sequence['ShellyController']
    ip_address: None = None
    channels: list["ShellyChannel"] = field(init=False)

    def __post_init__(self, channel_first_index: int) -> None:
        """Initialize."""
        print(f"Initializing {self}")
        self.session = requests.Session()
        self.channels = [
            channel
            for dimmer in self.dimmers
            for channel in dimmer.channels
        ]

    def __init_subclass__(cls, bulb_compatibility: type[Bulb]) -> None:
        """"""
        cls.bulb_compatibility = bulb_compatibility

    def update_channels(self, updates: Sequence['ChannelUpdate'], force: bool):
        """Effect updates, optionally forcing the updates 
           regardless of believed state."""
        
        # FORCE IS CURRENTLY IGNORED !!!!!
        filtered_updates = updates
        asyncio.run(self._execute_commands(filtered_updates))

    def set_channel(
        self, 
        channel: 'ShellyChannel',
        brightness: int | None,
        transition: float | None,
        color: Color | None,
        on: bool | None,
    ) -> None:
        """Build and send command via requests.
           Does not check current state."""
        update = ChannelUpdate(
            channel=channel,
            brightness=brightness,
            trans=transition,
            color=color,
            on=on,
        )
        command = self._make_set_command(update)
        response = self.session.get(
            url=command.url,
            params=command.params,
            timeout=1.0,
        )
        response.raise_for_status()
        channel.update_state(update)

    async def _execute_command(
        self, 
        update: 'ChannelUpdate'
    ) -> aiohttp.ClientResponse:
        """ Send individual command as part of asynchonous batch. """
        command = self._make_set_command(update)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=command.url,
                params=command.params,
                raise_for_status=True,
            ) as response:
                response = await response.json()
        update.channel.update_state(update)
        return response
    
    def _make_set_command(self, update: ChannelUpdate) -> '_ChannelCommand':
        """Produce dimmer API parameters from provided update."""
        assert update.color is None
        _trans = (
            self.trans_min
                if update.trans is None else
            update.trans
        )
        params = (
            ({'id': update.channel.id}) |
            ({'brightness': update.brightness} 
                if update.brightness is not None else {}) |
            ({'trans_duration': _trans}
                if update.brightness is not None else {}) |
            ({'on': str(update.on).lower()}
                if update.on is not None else {})
        )
        return _ChannelCommand(
            channel = update.channel,
            url=f'http://{update.channel.ip_address}/rpc/Light.Set',
            params=params,
        )

    async def _execute_commands(
        self,
        updates: Sequence['ChannelUpdate'],
    ) -> list[aiohttp.ClientResponse]:
        """Execute multiple commands asynchronously."""
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self._execute_command(update))
                for update in updates
            ]
        return [task.result() for task in tasks]


@dataclass
class ShellyDimmer(LightController, ABC, bulb_compatibility=DimBulb):
    """Set up Shelly dimmer and channels.
       Everything else handled by parent controller and child channels."""

    # channels: list["ShellyChannel"] = field(init=False)

    def __post_init__(self, channel_first_index) -> None:
        """Initialize."""
        print(f"Initializing {self}")
        self.session = requests.Session()
        try:
            self.channels = [
                ShellyChannel(
                    index=channel_first_index + id,
                    id=id, 
                    ip_address=self.ip_address,
                    session=self.session,
                    brightness=status['brightness'],
                    color=None,
                    on=status['output']
                ) 
                for id, status in self._get_state_of_channels()
            ]
        except requests.exceptions.Timeout as e:
            print(f"*** Failed to reach '{self.ip_address}' ***")
            print(f"*** Error: {e} ***")
            raise OSError from None

    def __init_subclass__(cls, bulb_compatibility: type[Bulb]) -> None:
        """"""
        cls.bulb_compatibility = bulb_compatibility

    def _get_state_of_channels(self) -> list[tuple[int, dict]]:
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
    
    def set_channel(
        self, 
        channel: LightChannel,
        brightness: int | None,
        transition: float | None,
        color: Color | None,
        on: bool | None,
    ) -> None:
        """Build and send command via requests.
           Does not check current state."""
        raise NotImplementedError()


@dataclass
class ShellyChannel(LightChannel):
    """ Models a single Shelly dimmer channel (light). """

    def calibrate(self) -> None:
        """Initiate channel calibration."""
        command = _ChannelCommand(
            channel = self,
            url=f'http://{self.ip_address}/rpc/Light.Calibrate',
            params={'id':self.id},
        )
        response = self.session.get(
            url=command.url,
            params=command.params,
            timeout=1.0,
        )
        response.raise_for_status()

    def update_state(self, update: ChannelUpdate):
        """Once the command has been sent without error,
           update the tracked state accordingly."""
        for attr in ('brightness', 'color', 'on'):
            value = getattr(update, attr)
            if value is not None:
                setattr(self, attr, value)


@dataclass
class ShellyProDimmer2PM(ShellyDimmer, channel_count=2):
    """Supports the Shelly Pro Dimmer 2PM."""

