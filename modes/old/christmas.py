"""Marquee Lighted Sign Project - signs_song"""

from typing_extensions import override

from device_defs import ALL_OFF, ALL_LOW, ALL_ON
from ..abstract.musicmode import MusicMode
from ..sequences import all_on, blink_all, random_each
from music import (
    set_mode,
    actions, bells, drums, sequences,
    dimmer_sequence_flip, section, Section, sequence,
)
from devices.specialparams import ActionParams, ChannelParams


class ChristmasSongs(MusicMode):
    """Christmas songs."""

    @override
    def execute(self) -> None:
        """Perform Christmas songs."""
        set_mode(self)
        songs: list[Section] = [
            self.jingle_bells(),
        ]
        for song in songs:
            song.play()

    def jingle_bells(self) -> Section:
        """Jingle Bells."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            bells(
                #  Jingle Bells, Jingle Bells,
                '  b♩ b♩   b♩ 𝄽 | b♩ b♩   b♩ 𝄽 | '
                
                #  Jingle all the   way 
                '  b♩ d♩   G♩ 𝄾 a♪ | b♩ 𝄽 𝄽 𝄽 |  '
                
                # Oh what fun it    is to ride in a 
                ' c♩ c♩    c♩ 𝄿 c♪ | c♩ b♩ b♩    b♪ b♪ |'

                # one horse open  sleigh
                ' b♩  a♩    a♩ b♩ | a♩ 𝄽 d♩ 𝄽 |'

                #  Jingle Bells, Jingle Bells,
                '  b♩ b♩   b♩ 𝄽 | b♩ b♩   b♩ 𝄽 | '
                
                #  Jingle all the   way 
                '  b♩ d♩   G♩ 𝄾 a♪ | b♩ 𝄽 𝄽 𝄽 |  '
                
                # Oh what fun it    is to ride in a 
                ' c♩ c♩    c♩ 𝄿 c♪ | c♩ b♩ b♩    b♪ b♪ |'

                # one horse open  sleigh
                ' d♩  d♩    b♩ G♩ | G♩ 𝄽 𝄽 𝄽 |'
            ),
            tempo=75,
        )

