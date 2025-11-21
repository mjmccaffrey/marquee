"""Marquee Lighted Sign Project - lightcontroller"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, InitVar
from collections.abc import Sequence
from typing import ClassVar

import requests

from bulb import Bulb

@dataclass
class LightController(ABC):
    """ABC for any light controller."""

    bulb_compatibility: ClassVar[type[Bulb]]
    trans_def: ClassVar[float]
    trans_min: ClassVar[float]
    trans_max: ClassVar[float]

    index: int
    ip_address: str
    bulb_model: Bulb
    channel_count: int
    channel_first_index: InitVar[int]
    session: requests.Session = field(init=False)
    channels: list['LightChannel'] = field(init=False)

    def __init_subclass__(cls, bulb_compatibility: type[Bulb]) -> None:
        cls.bulb_compatibility = bulb_compatibility

    def __post_init__(self, channel_first_index: int) -> None:
        """Ensure bulb compatibility"""
        if not isinstance(self.bulb_model, type(self.bulb_compatibility)):
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

    @abstractmethod
    def set_channel(
        self, 
        channel: 'LightChannel',
        brightness: int | None,
        transition: float | None,
        color: 'Color | None',
        on: bool | None,
    ) -> None:
        """Build and send command via requests.
           Does not check current state."""

@dataclass
class LightChannel(ABC):
    """Protocol for any controller channel (light)."""

    index: int
    id: int
    ip_address: str
    session: requests.Session
    brightness: int # = field(init=False)
    color: 'Color | None' # = field(init=False)
    on: bool # = field(init=False)

    @abstractmethod
    def calibrate(self) -> None:
        """Initiate channel calibration."""

    def update_state(self, update: 'ChannelUpdate'):
        """Once the command has been sent without error,
           update the tracked state accordingly."""


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

@dataclass
class ChannelUpdate:
    """"""
    channel: LightChannel
    brightness: int | None
    trans: float | None
    color: Color | None
    on: bool | None

@dataclass
class _ChannelCommand:
    """ Parameters for giving command to dimmer. """
    channel: 'LightChannel'
    url: str
    params: dict

