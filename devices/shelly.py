"""Marquee Lighted Sign Project - shelly"""

from abc import ABC
import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field
import time
import logging
from typing import ClassVar

import aiohttp
import requests

from color import Color
from .bulb import DimBulb
from .lightcontroller import (
    ChannelUpdate, ChannelCommand, LightController, LightChannel,
)

log = logging.getLogger('marquee.shelly')


@dataclass(kw_only=True)
class ShellyController(LightController, bulb_comp=DimBulb):
    """Virtual consolidated controller."""

    trans_min: ClassVar[float] = 0.5
    all_at_once: ClassVar[bool] = False

    channel_count: int = field(init=False)
    dimmers: Sequence[LightController]
    channel_first_index: None = None
    index: None = None
    ip_address: None = None

    def __post_init__(self) -> None:
        """Initialize."""
        log.info(f"Initializing {self}")
        super().__post_init__()
        self.session = requests.Session()
        self.channels = [
            channel
            for dimmer in self.dimmers
            for channel in dimmer.channels
        ]
        self.channel_count = len(self.channels)

    def __str__(self) -> str:
        return f"{type(self).__name__}"
    
    def calibrate(self) -> None:
        """Execute calibration on each successive channel."""
        time.sleep(3)
        max_channel = max(
            d.channel_count for d in self.dimmers
        )
        for id in range(max_channel):
            log.info(f"Calibrating channel {id}")
            for dimmer in self.dimmers:
                if id < dimmer.channel_count:
                    dimmer.channels[id].calibrate()
            time.sleep(150)
        log.info("Calibration should be complete")

    def execute_channel_updates(self, updates: Sequence['ChannelUpdate']) -> None:
        """Build and send commands via aiohttp asynchronously."""
        asyncio.run(self._execute_commands(updates))

    def execute_update_all_at_once(self, update: 'ChannelUpdate'):
        """Update the 'all' zone, rather than individual channels.
           Not supported on these devices."""
        raise ValueError("Method should not have been called.")

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

    async def _execute_command(
        self, 
        update: 'ChannelUpdate'
    ) -> aiohttp.ClientResponse:
        """Send individual command as part of asynchronous batch.
           Update channel state."""
        command = update.channel._make_set_command(update)
        # log.info(
        #     command.channel.index,
        #     command.channel.controller.ip_address,
        #     command.url,
        #     command.params
        # )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=command.url,
                params=command.params,
                raise_for_status=True,
            ) as response:
                response = await response.json()
        update.channel.update_state(update)
        return response
    
    
@dataclass(kw_only=True)
class ShellyDimmer(LightController, ABC, bulb_comp=DimBulb):
    """Set up Shelly dimmer and channels.
       Everything else handled by parent controller and child channels."""

    trans_min: ClassVar[float] = 0.5
    all_at_once: ClassVar[bool] = False

    def __init_subclass__(cls, channel_count: int) -> None:
        """Set channel count for concrete subclasses."""
        cls.channel_count = channel_count

    def __post_init__(self) -> None:
        """Initialize."""
        log.info(f"Initializing {self}")
        super().__post_init__()
        self.session = requests.Session()
        try:
            self.channels = [
                ShellyChannel(
                    index=self.channel_first_index + id,
                    id=str(id), 
                    controller=self,
                    brightness=status['brightness'],
                    color=None,
                    on=status['output']
                ) 
                for id, status in self._get_state_of_channels()
            ]
        except requests.exceptions.Timeout as e:
            log.info(f"*** Failed to reach '{self.ip_address}' ***")
            log.info(f"*** Error: {e} ***")
            raise OSError from None

    def _get_state_of_channels(self) -> list[tuple[int, dict]]:
        """Fetch status parameters for all channels."""
        result = self.session.get(
            url=f'http://{self.ip_address}/rpc/Shelly.GetStatus',
            timeout=1.0,
        )
        json = result.json()
        return [
            (id, json[f'light:{id}'])
            for id in range(self.channel_count)
        ]      
    
    def calibrate(self) -> None:
        """Calibrate all channels."""
        raise ValueError("Method should not have been called.")

    def execute_channel_updates(self, updates: Sequence['ChannelUpdate']) -> None:
        """Build and send commands via aiohttp asynchronously.
           Use method in ShellyController instead."""
        raise NotImplementedError()

    def execute_update_all_at_once(self, update: 'ChannelUpdate'):
        """Update the 'all' zone, rather than individual channels.
           Not supported on these devices."""
        raise ValueError("Method should not have been called.")


@dataclass(kw_only=True)
class ShellyChannel(LightChannel):
    """ Models a single Shelly dimmer channel (light). """

    brightness: int

    def calibrate(self) -> None:
        """Initiate channel calibration."""
        command = ChannelCommand(
            channel = self,
            url=f'http://{self.controller.ip_address}/rpc/Light.Calibrate',
            params={'id': self.id},
        )
        response = self.controller.session.get(
            url=command.url,
            params=command.params,
            timeout=1.0,
        )
        response.raise_for_status()

    def _make_set_command(self, update: ChannelUpdate) -> 'ChannelCommand':
        """Produce dimmer API parameters from provided update.
           Color is ignored."""
        _trans = (
            self.controller.trans_min
                if update.transition is None else
            update.transition
        )
        params = (
            ({'id': update.channel.id}) |
            ({'brightness': update.brightness} 
                if update.brightness is not None else {}) |
            ({'transition_duration': _trans}
                if update.brightness is not None else {}) |
            ({'on': str(update.on).lower()}
                if update.on is not None else {})
        )
        return ChannelCommand(
            channel = update.channel,
            url=f'http://{self.controller.ip_address}/rpc/Light.Set',
            params=params,
        )

    def _set(
        self, 
        brightness: int | None,
        transition: float | None,
        color: Color | None,
        on: bool | None,
    ) -> None:
        """Build and send command via requests.
           Does not check current state."""
        update = ChannelUpdate(
            channel=self,
            brightness=brightness,
            transition=transition,
            color=color,
            on=on,
        )
        command = self._make_set_command(update)
        response = self.controller.session.get(
            url=command.url,
            params=command.params,
            timeout=1.0,
        )
        response.raise_for_status()
        self.update_state(update)


@dataclass(kw_only=True)
class ShellyProDimmer1PM(ShellyDimmer, channel_count=1):
    """Supports the Shelly Pro Dimmer 1PM."""


@dataclass(kw_only=True)
class ShellyProDimmer2PM(ShellyDimmer, channel_count=2):
    """Supports the Shelly Pro Dimmer 2PM."""

