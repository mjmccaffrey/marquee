# 1: https://192.168.64.121/clip/v2/resource/light/ca051ade-5842-4c15-aacf-b1e795feb1ad?on=on&dynamics=duration
# 2: on state not being saved

"""Marquee Lighted Sign Project - hue"""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace
import logging
from typing import ClassVar

import requests
import urllib3

from color import Color, XY
from .bulb import HueBulb
from .lightcontroller import (
    ChannelUpdate, ChannelCommand, LightController, LightChannel,
)

log = logging.getLogger(__name__)


@dataclass(kw_only=True, repr=False)
class HueBridge(LightController, bulb_comp=HueBulb):
    """Hue bridge controller."""

    trans_min: ClassVar[float] = 0.0  # ?????????
    all_at_once: ClassVar[bool] = True

    application_key: str
    bulb_ids: Sequence[str]
    zone_ids: Sequence[str]
    channel_count: int = field(init=False)
    channel_first_index: None = None

    def __init_subclass__(cls, channel_count: int) -> None:
        """Set channel count for concrete subclasses."""
        cls.channel_count = channel_count

    def __post_init__(self) -> None:
        """Initialize."""
        log.info(f"Initializing {self}")
        super().__post_init__()
        self.session = requests.Session()
        self.session.headers = {'hue-application-key': self.application_key}
        self.session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        assert isinstance(self.bulb_model, HueBulb)
        try:
            self.get_state_of_channels()
        except requests.exceptions.Timeout as e:
            log.info(f"*** Failed to reach '{self.ip_address}' ***")
            log.info(f"*** Error: {e} ***")
            raise OSError from None

    def get_state_of_channels(self) -> None:
        """Fetch status parameters for all channels."""
        result = self.session.get(
            url=f'https://{self.ip_address}/clip/v2/resource/light',
            timeout=2.0,
        )
        result.raise_for_status()
        json = result.json()
        lights = {
            light['id']: light
            for light in json['data']
        }
        self.channels = [
            HueChannel(
                index=i,
                id=id,
                controller=self,
                brightness=lights[id]['dimming']['brightness'],
                color=XY(
                    x=lights[id]['color']['xy']['x'],
                    y=lights[id]['color']['xy']['y'],
                ),
                on=lights[id]['on']['on'],
            )
            for i, id in enumerate(self.bulb_ids)
        ]
        self.channel_count = len(self.channels)
    
    def calibrate(self) -> None:
        """Calibrate all channels."""
        raise NotImplementedError

    def execute_channel_updates(self, updates: Sequence['ChannelUpdate']) -> None:
        """Build and send commands."""
        for update in updates:
            command = update.channel._make_set_command(update)
            response = self.session.put(
                url=command.url,
                json=command.params,
                timeout=2.0,
            )
            # log.info('*********')
            # log.info(command.url)
            # log.info(command.params)
            # log.info('*********')
            response.raise_for_status()
            update.channel.update_state(update)

    def execute_update_all_at_once(self, update: 'ChannelUpdate'):
        """Update the 'all' zone, rather than individual channels.
           Does not check current state."""
        command = update.channel._make_set_command(update)
        for i, id in enumerate(self.zone_ids):
            response = self.session.put(
                url=f'https://{self.ip_address}/clip/v2/resource/grouped_light/{id}',
                json=command.params,
                timeout=2.0,
            )
            log.info("ZONE: ", i, command.params)
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
                    if update.transition is None else
             update.transition
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
            ({'dynamics': {'duration': transition}}
                if update.transition is not None else {})  # !!!!!!!!!
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
            transition=transition,
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

