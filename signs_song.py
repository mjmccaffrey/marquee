"""Marquee Lighted Sign Project - Signs Song"""

import sys
import time

from configuration import ALL_HIGH, ALL_OFF, ALL_LOW, ALL_ON
from modes import PlayMusicMode
from music import (
    dimmer, dimmer_sequence, light, measure, part, play,
    section, sequence,
)
from music import(
    act, act_part, bell_part, drum_part,
    rest, sequence_measure, sequence_part
)
from sequences import blink_all
from specialparams import ActionParams, DimmerParams, SpecialParams

class SignsSong(PlayMusicMode):
    """Signs song."""

    def execute(self):
        """Perform Signs song."""
        self.player.lights.set_relays(ALL_OFF)
        time.sleep(5)
        sections = [
            self.intro(),
            self.refrain_1(),
        ]
        for section in sections:
            section.play(tempo=60)
        sys.exit()

    def intro(self):
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
            ),  
            bell_part(
                #                     And the
                '  𝄻 | 𝄻 |  𝄻 |  𝄼 𝄽 𝄾 a𝅘𝅥𝅯 b𝅘𝅥𝅯 |'
                
                # sign says long-haired freaky people 
                '  c♩ c♩     b♪ b♪      b♪ b𝅘𝅥𝅯 G𝅘𝅥𝅯  |  '
                
                # need not apply  so I
                ' 𝄾 a♪ a♪ 𝄿 G𝅘𝅥𝅯 𝄽 𝄾 a𝅘𝅥𝅯 a𝅘𝅥𝅯  |'

                # tucked my hair up under my hat and I
                '𝄿 a♪    a𝅘𝅥𝅯 a♪   a♪  b♪ a♪ a♪ d𝅘𝅥𝅯 b𝅘𝅥𝅯 |'

                # went in to ask him why
                ' d𝅘𝅥𝅯 d♪   b𝅘𝅥𝅯 d♪ d♪ b𝅘𝅥𝅯 a𝅘𝅥𝅯 𝄾 𝄽 |'

                # He said, you look like a fine, upstanding young
                '  𝄿 e𝅘𝅥𝅯 e𝅘𝅥𝅯 𝄿   e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 d𝅘𝅥𝅯   𝄾 c♪    c♪ d♪ |'

                # man,  I think you'll do, uh, so I
                ' d𝅘𝅥𝅯 c♪ a𝅘𝅥𝅯 d♪   d♪     c♩  𝄿 a𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  |'

                # took off my hat and said imagine that, huh
                ' e𝅘𝅥𝅯   e♪  c𝅘𝅥𝅯 e♪      c♪   d𝅘𝅥𝅯 d𝅘𝅥𝅯   d♪    𝄿 e𝅘𝅥𝅯  𝄾 |'

                # me, working for you,    Oh...
                '  c♪ 𝄾  c𝅘𝅥𝅯 a𝅘𝅥𝅯 c𝅘𝅥𝅯 d𝅘𝅥𝅯  𝄽  𝄾  G♪  '  # e♪ 𝄿 e𝅘𝅥𝅯 d𝅘𝅥𝅯 e𝅘𝅥𝅯 d♪ | '
            )
        )

    def refrain_1(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drum_part(
                '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |  '
            ),
            sequence_part(
                '  𝄻 |  '
                # Sign, sign, everywhere a sign
                # OnOff On, fade down
                '  ♪ ♪ ♩  | ♩  ',
                 sequence(blink_all),
            ),
            bell_part(
                # '  𝄻 |  '
                # '  D♪ D♪ D♪ D♪ |  '
                # '  𝄽 𝄽 eca♪ eca♪ eEG♪ eEG♪ |  '
                # Sign, sign, everywhere a sign
                '  e♩  e♩  d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  c♩ |  '
                # Blockin' out the scenery, breakin' my mind
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯   e𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪   a𝅘𝅥𝅯 c𝅘𝅥𝅯 c♪ c♩ |  '
                # Do this, don't do that, can't you read the sign?
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 𝄿 e𝅘𝅥𝅯   𝄿 e𝅘𝅥𝅯 c𝅘𝅥𝅯 d𝅘𝅥𝅯   𝄿 de𝅘𝅥𝅯 de𝅘𝅥𝅯 de𝅘𝅥𝅯    𝄿 d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 |' # 𝄾 d♩   '
            ),
        )
 
     # def full_first_verse(self):
    #     # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
    #     return section(
    #         drum_part(
    #             '  h𝅝> | '
    #              '  lh♩ lh♩ lh♩ lh♩ | l♪ h♪ l♪ h♪ l♪ h♪ l♪ h♪|'
    #              '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
    #              '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
    #              '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
    #              '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
    #              '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
    #              '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  ',
    #         ),  
    #         bell_part(
    #             #                     And the
    #             '  𝄻 | 𝄻 |  𝄻 |  𝄼 𝄽 𝄾 a𝅘𝅥𝅯 b𝅘𝅥𝅯 |'
                
    #             # sign says long-haired freaky people need not apply  so I
    #             'c♩ c♩       b♪ b♪       c𝅘𝅥𝅯 a𝅘𝅥𝅯 b𝅘𝅥𝅯 G𝅘𝅥𝅯 | 𝄾 a♪ a♪ a𝅘𝅥𝅯 G𝅘𝅥𝅯 𝄽 𝄾 a𝅘𝅥𝅯 a𝅘𝅥𝅯 |'

    #             # tucked my hair up under my hat and I
    #             '𝄿 a♪    a𝅘𝅥𝅯 a♪   a𝅘𝅥𝅯 b♪ a𝅘𝅥𝅯 a𝅘𝅥𝅯 a𝅘𝅥𝅯 𝄾 d𝅘𝅥𝅯 b𝅘𝅥𝅯 |'

    #             # went in to ask him why
    #             ' d𝅘𝅥𝅯 d♪   b𝅘𝅥𝅯 d♪ d♪ b𝅘𝅥𝅯 a𝅘𝅥𝅯 𝄾 𝄽 |'

    #             # He said, you look like a fine, upstanding young
    #             ' 𝄿 d𝅘𝅥𝅯 d𝅘𝅥𝅯  d𝅘𝅥𝅯  d𝅘𝅥𝅯   d𝅘𝅥𝅯   d𝅘𝅥𝅯 e𝅘𝅥𝅯 d♪ d♪ d𝅘𝅥𝅯 d𝅘𝅥𝅯 e♪ |'

    #             # man, I think you'll do, uh, so I
    #             ' e𝅘𝅥𝅯 d♪ b𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 d𝅘𝅥𝅯 d𝅘𝅥𝅯 𝄽 𝄿 b𝅘𝅥𝅯 d𝅘𝅥𝅯 b𝅘𝅥𝅯 |'

    #             # took off my hat and said imagine that, huh
    #             ' d𝅘𝅥𝅯   d♪  d𝅘𝅥𝅯 d𝅘𝅥𝅯  d𝅘𝅥𝅯  d𝅘𝅥𝅯   b𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 e♪ 𝄿 d𝅘𝅥𝅯 𝄾 |'

    #             # me, a-working for you,    Oh...
    #             ' d♪ 𝄿 b𝅘𝅥𝅯 d𝅘𝅥𝅯 d𝅘𝅥𝅯 d𝅘𝅥𝅯 d𝅘𝅥𝅯 e♪ 𝄿 e𝅘𝅥𝅯 d𝅘𝅥𝅯 e𝅘𝅥𝅯 d♪ | '
    #         )
    #     )

