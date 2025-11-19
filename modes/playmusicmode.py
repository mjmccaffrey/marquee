"""Marquee Lighted Sign Project - playmusicmode"""

from dataclasses import dataclass

from music import set_player
from .playmode import PlayMode


@dataclass
class PlayMusicMode(PlayMode):
    """Base for playing music."""

    def __post_init__(self) -> None:
        """Initialize."""
        # self.preset_devices(
        #     channels = not isinstance(self.special, ChannelParams),
        #     relays = isinstance(self.special, ChannelParams),
        # )
        set_player(self.player)

