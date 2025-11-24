"""Marquee Lighted Sign Project - lightcontroller"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, InitVar
from collections.abc import Sequence
from typing import ClassVar

import requests

from bulb import Bulb

@dataclass(kw_only=True)
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

    @abstractmethod
    def update_channels(self, updates: Sequence['ChannelUpdate'], force: bool):
        """Effect updates, optionally forcing the updates 
           regardless of believed state."""

@dataclass(kw_only=True)
class LightChannel(ABC):
    """Protocol for any controller channel (light)."""

    index: int
    id: int
    controller: LightController
    brightness: int # = field(init=False)
    color: 'Color | None' # = field(init=False)
    on: bool # = field(init=False)

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
        color: 'Color | None',
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
            for attr in channel_state_attrs
        )

    def update_channels(self, updates: Sequence['ChannelUpdate'], force: bool):
        """Effect updates, optionally forcing the updates 
           regardless of believed state."""
        if not force:
            updates = [
                update 
                for update in updates
                if update.channel.update_needed(update)
            ]

    def update_state(self, update: 'ChannelUpdate'):
        """Once the command has been sent without error,
           update the tracked state accordingly."""
        for attr in channel_state_attrs:
            value = getattr(update, attr)
            if value is not None:
                setattr(self, attr, value)


@dataclass
class Color:
    """Color specification."""

@dataclass
class RGB(Color):
    """ RGB color. """
    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        """"""
        # _xy = CONVERT RGB TO XY

@dataclass
class XY(Color):
    """ XY color. """
    x: float
    y: float

channel_state_attrs = ('brightness', 'color', 'on')

@dataclass
class ChannelUpdate:
    """"""
    channel: LightChannel
    brightness: int | None
    trans: float | None
    color: Color | None
    on: bool | None

@dataclass
class ChannelCommand:
    """ Parameters for giving command to dimmer. """
    channel: 'LightChannel'
    url: str
    params: dict

