"""Marquee Lighted Sign Project - lightcontroller"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import Sequence
from typing import ClassVar

import requests

from bulb import Bulb
from color import Color

@dataclass(kw_only=True, repr=False)
class LightController(ABC):
    """ABC for any light controller."""

    bulb_comp: ClassVar[type[Bulb]]
    channel_count: ClassVar[int]
    trans_min: ClassVar[float]
    trans_max: ClassVar[float]

    index: int
    ip_address: str
    bulb_model: Bulb
    channel_first_index: int
    session: requests.Session = field(init=False)
    channels: Sequence['LightChannel'] = field(init=False)

    def __init_subclass__(cls, bulb_comp: type[Bulb]) -> None:
        cls.bulb_comp = bulb_comp

    def __post_init__(self) -> None:
        """Ensure bulb compatibility"""
        if not isinstance(self.bulb_model, type(self.bulb_comp)):
            raise TypeError(
                f"Incompatible bulb model {self.bulb_model} "
                f"for controller {type(self).__name__}."
            )

    def __str__(self) -> str:
        return f"{type(self).__name__} {self.index} @ {self.ip_address}"
    
    def __repr__(self) -> str:
        return f"<{self}>"
    
    def close(self) -> None:
        """Clean up."""

    def update_channels(self, updates: Sequence['ChannelUpdate'], force: bool = False):
        """Effect updates, optionally forcing the updates 
           regardless of believed state."""
        if force:
            updates_to_send = updates
        else:
            updates_to_send = [
                update 
                for update in updates
                if update.channel.update_needed(update)
            ]
            # print("UPDATE_CHANNELS:")
            # for u in updates_to_send:
            #     print("  ", u)
        self.execute_updates(updates=updates_to_send)

    @abstractmethod
    def execute_updates(self, updates: Sequence['ChannelUpdate']) -> None:
        """Build and send commands via aiohttp asynchronously."""


@dataclass(kw_only=True, repr=False)
class LightChannel(ABC):
    """Protocol for any controller channel (light)."""

    index: int
    id: str
    controller: LightController
    brightness: int | float
    color: Color | None
    on: bool

    STATE_ATTRS = ('brightness', 'color', 'on')

    def __repr__(self):
        return f"Channel {self.index}"
    
    @abstractmethod
    def calibrate(self) -> None:
        """Initiate channel calibration."""

    @abstractmethod
    def _make_set_command(self, update: 'ChannelUpdate') -> 'ChannelCommand':
        """Produce dimmer API parameters from provided update."""

    @abstractmethod
    def _set(
        self, 
        brightness: int | None,
        transition: float | None,
        color: Color | None,
        on: bool | None,
    ) -> None:
        """Build and send command via requests.
           Does not check current state."""

    def update_needed(self, update: 'ChannelUpdate'):
        """Return False if all desired states match
           current states, else True."""
        return any(
            (value := getattr(update, attr)) is not None and
            value != getattr(self, attr)
            for attr in self.STATE_ATTRS
        )

    def update_state(self, update: 'ChannelUpdate'):
        """Once the command has been sent without error,
           update the tracked state accordingly."""
        print("UPDATE STATE")
        if update.brightness is not None:
            self.brightness = update.brightness
        if update.color is not None:
            self.color = update.color
        if update.on is not None:
            self.on = update.on


@dataclass
class ChannelUpdate:
    """"""
    channel: LightChannel
    brightness: int | None = None
    trans: float | None = None
    color: Color | None = None
    on: bool | None = None

@dataclass
class ChannelCommand:
    """ Parameters for giving command to dimmer. """
    channel: 'LightChannel'
    url: str
    params: dict

