"""Marquee Lighted Sign Project - hue"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

import requests

from bulb import HueBulb
from color import Color
from lightcontroller import (
    ChannelUpdate, ChannelCommand, 
    LightController, LightChannel,
)

@dataclass(kw_only=True)
class HueBridge(LightController, bulb_comp=HueBulb):
    """Hue bridge controller."""

    trans_min: ClassVar[float] = 0.5
    trans_max: ClassVar[float] = 10800.0

    bulb_ids: Sequence[str]
    channel_count: int = field(init=False)
    channel_first_index: None = None
    index: None = None

    def __post_init__(self) -> None:
        """Initialize."""
        print(f"Initializing {self}")
        self.session = requests.Session()
        try:
            lights = self._get_state_of_channels()
        except requests.exceptions.Timeout as e:
            print(f"*** Failed to reach '{self.ip_address}' ***")
            print(f"*** Error: {e} ***")
            raise OSError from None

        self.channels = [
            HueChannel(
                index=i,
                id=id,
                controller=self,
                brightness=lights['dimming']['brightness'],
                color=lights['color']['xy'],
                on=lights['on']['on'],
            )
            for i, id in enumerate(self.bulb_ids)
        ]
        self.channel_count = len(self.channels)

    def _get_state_of_channels(self) -> dict[str, dict]:
        """Fetch status parameters for all channels."""
        result = self.session.get(
            url=f'https://{self.ip_address}/resource/light',
            timeout=1.0,
        )
        json = result.json()
        return {
            light['id']: light
            for light in json['data']
        }
    
    def __init_subclass__(cls, channel_count: int) -> None:
        """Set channel count for concrete subclasses."""
        cls.channel_count = channel_count

    def execute_updates(self, updates: Sequence['ChannelUpdate']) -> None:
        """Build and send commands."""
        for update in updates:
            command = update.channel._make_set_command(update)
            response = self.session.put(
                url=command.url,
                json=command.params,
                timeout=1.0,
            )
            response.raise_for_status()


@dataclass(kw_only=True)
class HueChannel(LightChannel):
    """ Models a single Hue channel (light). """

    brightness: float

    def calibrate(self) -> None:
        """Initiate channel calibration."""
        raise NotImplementedError

    def _make_set_command(self, update: ChannelUpdate) -> 'ChannelCommand':
        """Produce dimmer API parameters from provided update."""
        _trans = (
            self.controller.trans_min
                if update.trans is None else
            update.trans
        )
        params = (
            ({'id': update.channel.id}) |
            ({'dimming': {'brightness': update.brightness}} 
                if update.brightness is not None else {}) |
            ({'trans_duration': _trans}
                if update.brightness is not None else {}) |
            ({'on': {'on': str(update.on).lower()}}
                if update.on is not None else {})
        )
        return ChannelCommand(
            channel = update.channel,
            url=f'http://{self.controller.ip_address}/resource/light/{self.id}',
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
            trans=transition,
            color=color,
            on=on,
        )
        command = self._make_set_command(update)
        response = self.controller.session.put(
            url=command.url,
            params=command.params,
            timeout=1.0,
        )
        response.raise_for_status()
        self.update_state(update)

