# 1: https://192.168.64.121/clip/v2/resource/light/ca051ade-5842-4c15-aacf-b1e795feb1ad?on=on&dynamics=duration
# 2: on state not being saved

"""Marquee Lighted Sign Project - hue"""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from typing import ClassVar

import requests
import urllib3

from bulb import HueBulb
from color import Color
from lightcontroller import (
    ChannelUpdate, ChannelCommand, 
    LightController, LightChannel,
)

@dataclass(kw_only=True, repr=False)
class HueBridge(LightController, bulb_comp=HueBulb):
    """Hue bridge controller."""

    trans_min: ClassVar[float] = 0.0  # ?????????
    trans_max: ClassVar[float] = 10800.0  # ?????????
    all_at_once: ClassVar[bool] = True

    application_key: str
    bulb_ids: Sequence[str]
    zone_ids: Sequence[str]
    channel_count: int = field(init=False)
    channel_first_index: None = None
    index: None = None

    def __post_init__(self) -> None:
        """Initialize."""
        print(f"Initializing {self}")
        super().__post_init__()
        self.session = requests.Session()
        self.session.headers = {'hue-application-key': self.application_key}
        self.session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        assert isinstance(self.bulb_model, HueBulb)
        try:
            lights = self._get_state_of_channels()
            print(f"Received status for {len(lights)} lights.")
        except requests.exceptions.Timeout as e:
            print(f"*** Failed to reach '{self.ip_address}' ***")
            print(f"*** Error: {e} ***")
            raise OSError from None
        self.channels = [
            HueChannel(
                index=i,
                id=id,
                controller=self,
                brightness=lights[id]['dimming']['brightness'],
                color=lights[id]['color']['xy'],
                on=lights[id]['on']['on'],
            )
            for i, id in enumerate(self.bulb_ids)
        ]
        self.channel_count = len(self.channels)

    def _get_state_of_channels(self) -> dict[str, dict]:
        """Fetch status parameters for all channels."""
        result = self.session.get(
            url=f'https://{self.ip_address}/clip/v2/resource/light',
            timeout=2.0,
        )
        result.raise_for_status()
        json = result.json()
        return {
            light['id']: light
            for light in json['data']
        }
    
    def __init_subclass__(cls, channel_count: int) -> None:
        """Set channel count for concrete subclasses."""
        cls.channel_count = channel_count

    def execute_channel_updates(self, updates: Sequence['ChannelUpdate']) -> None:
        """Build and send commands."""
        for update in updates:
            command = update.channel._make_set_command(update)
            response = self.session.put(
                url=command.url,
                json=command.params,
                timeout=2.0,
            )
            # print('*********')
            # print(command.url)
            print(command.params)
            # print('*********')
            response.raise_for_status()
            update.channel.update_state(update)

    def execute_update_all_at_once(self, update: 'ChannelUpdate'):
        """Update the all zone, rather than individual channels.
           Does not check current state."""
        command = update.channel._make_set_command(update)
        for i, id in enumerate(self.zone_ids):
            response = self.session.put(
                url=f'https://{self.ip_address}/clip/v2/resource/grouped_light/{id}',
                json=command.params,
                timeout=2.0,
            )
            # print("ZONE: ", i, command.params)
            response.raise_for_status()
        for channel in self.channels:
            channel.update_state(replace(update, channel=channel))


@dataclass(kw_only=True, repr=False)
class HueChannel(LightChannel):
    """ Models a single Hue channel (light). """

    brightness: float

    def calibrate(self) -> None:
        """Initiate channel calibration."""
        raise NotImplementedError

    def _make_set_command(self, update: ChannelUpdate) -> 'ChannelCommand':
        """Produce dimmer API parameters from provided update."""
        transition = int(
            (self.controller.trans_min
                    if update.trans is None else
             update.trans
            ) * 1000
        )
        params = (
            ({'color': {'xy': {
                    'x': update.color.x,
                    'y': update.color.y,}}}
                if update.color is not None else {}) | 
            ({'dimming': {'brightness': update.brightness}} 
                if update.brightness is not None else {}) |
            ({'on': {'on': update.on}}
                if update.on is not None else {}) |
            {'dynamics': {'duration': transition}}
        )
        return ChannelCommand(
            channel = update.channel,
            url=f'https://{self.controller.ip_address}/clip/v2/resource/light/{self.id}',
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
            timeout=2.0,
        )
        response.raise_for_status()
        self.update_state(update)

