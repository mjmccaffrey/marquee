"""Marquee Lighted Sign Project - Signs Song"""

import sys

from configuration import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from modes import PlayMusicMode
from music import (
    dimmer, dimmer_sequence, light, measure, part, play,
    section, sequence,
)
from music import(
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
            section.play(tempo=60)
        sys.exit()

    def intro(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            bell_part(
                #                     And the
                '  𝄻 | 𝄻 |  𝄻 |  𝄼 𝄽 𝄾 a𝅘𝅥𝅯 b𝅘𝅥𝅯 |'
                
                # sign says long-haired freaky people need not apply  so I
                'c♩ c♩       b♪ b♪       c𝅘𝅥𝅯 a𝅘𝅥𝅯 b𝅘𝅥𝅯 G𝅘𝅥𝅯 | 𝄾 a♪ a♪ a𝅘𝅥𝅯 G𝅘𝅥𝅯 𝄽 𝄾 a𝅘𝅥𝅯 a𝅘𝅥𝅯 |'

                # tucked my hair up under my hat and I
                '𝄿 a♪    a𝅘𝅥𝅯 a♪   a𝅘𝅥𝅯 b♪ a𝅘𝅥𝅯 a𝅘𝅥𝅯 a𝅘𝅥𝅯 𝄾 d𝅘𝅥𝅯 b𝅘𝅥𝅯 |'

                # went in to ask him why
                ' d𝅘𝅥𝅯 d♪   b𝅘𝅥𝅯 d♪ d♪ b𝅘𝅥𝅯 a𝅘𝅥𝅯 𝄾 𝄽 |'

                # He said, you look like a fine, upstanding young
                ' 𝄿 d𝅘𝅥𝅯 d𝅘𝅥𝅯  d𝅘𝅥𝅯  d𝅘𝅥𝅯   d𝅘𝅥𝅯   d𝅘𝅥𝅯 e𝅘𝅥𝅯 d♪ d♪ d𝅘𝅥𝅯 d𝅘𝅥𝅯 e♪ |'

                # man, I think you'll do, uh, so I
                ' e𝅘𝅥𝅯 d♪ b𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 d𝅘𝅥𝅯 d𝅘𝅥𝅯 𝄽 𝄿 b𝅘𝅥𝅯 d𝅘𝅥𝅯 b𝅘𝅥𝅯 |'

                # took off my hat and said imagine that, huh
                ' d𝅘𝅥𝅯   d♪  d𝅘𝅥𝅯 d𝅘𝅥𝅯  d𝅘𝅥𝅯  d𝅘𝅥𝅯   b𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 e♪ 𝄿 d𝅘𝅥𝅯 𝄾 |'

                # me, a-working for you,    Oh...
                ' d♪ 𝄿 b𝅘𝅥𝅯 d𝅘𝅥𝅯 d𝅘𝅥𝅯 d𝅘𝅥𝅯 d𝅘𝅥𝅯 e♪ 𝄿 e𝅘𝅥𝅯 d𝅘𝅥𝅯 e𝅘𝅥𝅯 d♪ | '
            )
        )

    def hook(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drum_part(
                '  h𝅝> | '
                 '  lh♩ lh♩ lh♩ lh♩ | l♪ h♪ l♪ h♪ l♪ h♪ l♪ h♪|'
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  ',
                accent=''
            ),  
            bell_part(
                # Sign, sign, everywhere a sign
                '  e♩  e♩  d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  c♩ |  '
                # Blockin' out the scenery, breakin' my mind
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯   e𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪   a𝅘𝅥𝅯 c𝅘𝅥𝅯 c♪ c♩ |  '
                # Do this, don't do that, can't you read the sign?
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 𝄿 e𝅘𝅥𝅯   𝄿 e𝅘𝅥𝅯 c𝅘𝅥𝅯 d𝅘𝅥𝅯   𝄿 de𝅘𝅥𝅯 de𝅘𝅥𝅯 de𝅘𝅥𝅯    𝄿 d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 | 𝄾 d♩   '
            )
            # sequence_part(
            #     "  𝄾 ♪ ♪ 𝄾 | 𝄾 ♪ ♪ 𝄾 | ♪ 𝄾 ♪ 𝄾 | 𝄾 ♪ ♪  ",
            #     sequence(blink_all, on_first=False),
            # ),
        )
 