"""Marquee Lighted Sign Project - Signs Song"""

import sys

from configuration import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from modes import PlayMusicMode
from music import (
    dimmer, dimmer_sequence, light, measure, part, play,
    section, sequence,
)
from notation import(
    act, act_part, bell_part, drum_part,
    rest, sequence_measure, sequence_part
)
from sequences import *

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
            # drum_part(
            #     '  h𝅝> | '
            #     #'  l♪ 𝄿 l𝅘𝅥𝅯  l𝅘𝅥𝅯 l𝅘𝅥𝅯 𝄿  l𝅘𝅥𝅯  l𝅘𝅥𝅯  l𝅘𝅥𝅯 𝄿  l𝅘𝅥𝅯  l𝅘𝅥𝅯  l𝅘𝅥𝅯 𝄿  l𝅘𝅥𝅯 |  ',
            #      '  lh♩ lh♩ lh♩ lh♩ | l♪ h♪ l♪ h♪ l♪ h♪ l♪ h♪|'
            #      '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
            #      '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  ',
            #     accent=''
            # ),  
            bell_part(
                # Intro
                '  𝄻 | 𝄻 | c♩ c♩ d𝅘𝅥𝅯 c♪ 𝄿 cG♩   eE𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪ ceG♩   dD𝅘𝅥𝅯 c♪ 𝄿 ceE♩ |  '
                # Sign, sign, everywhere a sign
                '  e♩  e♩  d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  c♩ |  '
                # Blockin' out the scenery, breakin' my mind
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯   e𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪   a𝅘𝅥𝅯 c𝅘𝅥𝅯 c♪ c♩ |  '
                # Do this, don't do that, can't you read the sign?
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 𝄿 e𝅘𝅥𝅯   𝄿 e𝅘𝅥𝅯 c𝅘𝅥𝅯 d𝅘𝅥𝅯   𝄿 de𝅘𝅥𝅯 de𝅘𝅥𝅯 de𝅘𝅥𝅯    𝄿 d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 | 𝄾 d♩   '
            ),
            # sequence_part(
            #     "  𝄾 ♪ ♪ 𝄾 | 𝄾 ♪ ♪ 𝄾 | ♪ 𝄾 ♪ 𝄾 | 𝄾 ♪ ♪  ",
            #     sequence(blink_all, on_first=False),
            # ),
        tempo=60,
        )
 