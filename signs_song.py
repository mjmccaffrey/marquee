"""Marquee Lighted Sign Project - Signs Song"""

import sys

from definitions import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from modes import PlayMusicMode
from music import (
    act, act_part, bell_part, dimmer, drum_part, light, measure, part, play, 
    rest, section, sequence, sequence_measure, sequence_part
)
from sequence_defs import *

class SignsSong(PlayMusicMode):
    """Signs song."""

    def execute(self):
        """Perform Signs song."""
        sections = [
            self.pre(),
        ]
        for section in sections:
            section.play()
        sys.exit()

    def pre(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            bell_part(
                '  e♩  e♩  d♪  c3𝅘𝅥𝅯 c3𝅘𝅥𝅯 a3𝅘𝅥𝅯  c♩  '
            ),
            sequence_part(
                '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  '
                '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  '
                '  𝅝 | 𝄻  ',
            ),
        tempo=70,
        )
    