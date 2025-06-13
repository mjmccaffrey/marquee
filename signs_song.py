"""Marquee Lighted Sign Project - Signs Song"""

import sys

from definitions import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from modes import PlayMusicMode
from music import (
    dimmer, dimmer_sequence, light, measure, part, play,
    section, sequence,
)
from notation import(
    act, act_part, drum_part, piano_part,
    rest, sequence_measure, sequence_part
)
from sequence_defs import *

class SignsSong(PlayMusicMode):
    """Signs song."""

    def execute(self):
        """Perform Signs song."""
        sections = [
            self.hook(),
        ]
        for section in sections:
            section.play()
        sys.exit()

    def hook(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            piano_part(
                '  e♩  e♩  d♪  c3𝅘𝅥𝅯 c3𝅘𝅥𝅯 a3𝅘𝅥𝅯  c♩  '
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯   e𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪ a♪ '
            ),
        tempo=70,
        )
