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
            self.refrain(1),
            self.transition(1),
            self.refrain(2),
        ]
        for section in sections:
            section.play(tempo=60)
        sys.exit()

    def intro(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drum_part(
                '  h𝅝> | '
                 '  lh♩ lh♩ lh♩ lh♩ | l♪ h♪ l♪ h♪ l♪ h♪ l♪ h♪|  ' #And the
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' #Sign says long-haired freaky people
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' #Need not apply so I
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' #Tucked my hair up under my hat and I
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 𝄿 𝄿 lh𝅘𝅥𝅯> l𝅘𝅥𝅯 𝄿 𝄿 hl♪ hl♪ lh♪ lh♪> |  ' #Went in to ask him why
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' #He said...
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' #Man, I think
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 𝄿 𝄿 lh𝅘𝅥𝅯> l𝅘𝅥𝅯 𝄿 𝄿 hl♪ hl♪ lh♪ lh♪> |  ' #Took off my hat...
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ | ', #Me, working for you
                 
            ),  
            bell_part(
                #                     And the
                '  𝄻 | 𝄻 |  𝄼 𝄽 𝄾 a𝅘𝅥𝅯 b𝅘𝅥𝅯 |'
                
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

    def refrain(self, play_thru: int):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        bells = bell_part(
            #'  𝄻 |  '
            # '  D♪ D♪ D♪ D♪ |  ' Build-up experiment
            # '  𝄽 𝄽 eca♪ eca♪ eEG♪ eEG♪ |  ' Build-up experiment
            # Sign, sign, everywhere a sign
            '  e♩  e♩  d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  c♩ |  '
            # Blockin' out the scenery, breakin' my mind
            '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯 e𝅘𝅥𝅯   e𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪   a𝅘𝅥𝅯 c𝅘𝅥𝅯 c♪ c♩ |  '
            # Do this, don't do that,   can't you read   the sign?
            '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 𝄿 e𝅘𝅥𝅯   𝄿 e𝅘𝅥𝅯 c𝅘𝅥𝅯 d𝅘𝅥𝅯 𝄿 de𝅘𝅥𝅯   de𝅘𝅥𝅯 de𝅘𝅥𝅯 d♪ c♪ | c♪ 𝄿 d𝅘𝅥𝅯 𝄽 𝄼 |' 
        )
        if play_thru == 1:
            return section(
                #drum_part(
                # for build-up    '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |  '
                #),
                # sequence_part(
                #     #'  𝄻 |  '
                #     # Sign, sign, everywhere a sign
                #     # OnOff On, fade down
                #     '  ♪ ♪ ♩  | ♩  ',
                #     sequence(blink_all),
                # ),
                bells,
            )
        else:
            return section(
                drum_part(
                # for build-up    '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |  '
                '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
                '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  '
                '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 |  ' 
                '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯 𝄼 | '                
                ),
                #sequence_part(
                    #'  𝄻 |  '
                    # Sign, sign, everywhere a sign
                    # OnOff On, fade down
                #    '  ♪ ♪ ♩  | ♩  ',
                #    sequence(blink_all),
                #),
            bells,
            )
 
    def transition (self, play_thru: int):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        if play_thru == 1:
            return section(
                drum_part(
                '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
               # '  lh♩ lh♩ lh♩ lh♩ | l♪ h♪ l♪ h♪ l♪ h♪ l♪ h♪|  '
                )
            )