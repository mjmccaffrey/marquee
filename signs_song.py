"""Marquee Lighted Sign Project - signs_song"""

import time

from configuration import ALL_HIGH, ALL_OFF, ALL_LOW, ALL_ON
from modes import PlayMusicMode
from music import (
    dimmer, dimmer_sequence, dimmer_sequence_flip, 
    light, measure, part, play,
    section, sequence,
)
from music import(
    act, act_part, bell_part, drum_part,
    sequence_measure, sequence_part
)
from sequences import blink_all, random_each
from definitions import ActionParams, DimmerParams, SpecialParams

class SignsSong(PlayMusicMode):
    """Signs song."""

    def execute(self):
        """Perform Signs song."""
        # self.player.lights.set_relays(ALL_OFF)
        time.sleep(1)
        sections = [
            self.intro(),
            self.refrain(1),
            self.transition(),
            self.refrain(2),
        ]
        for section in sections:
            section.play(tempo=75)
        self.player.wait(None)

    def intro(self):
        """Signs song intro."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drum_part(
                '  h𝅝> | '
                 '  lh♩ lh♩ lh♩ lh♩ | l♪ h♪ l♪ h♪ l♪ h♪ l♪ h♪|  ' # And the
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' # Sign says long-haired freaky people
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' # Need not apply so I
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' # Tucked my hair up under my hat and I
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 𝄿 𝄿 lh𝅘𝅥𝅯> l𝅘𝅥𝅯 𝄿 𝄿 hl♪ hl♪ lh♪ lh♪> |  ' # Went in to ask him why
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' # He said...
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ |  ' # Man, I think
                 '  lh𝅘𝅥𝅯> l𝅘𝅥𝅯 𝄿 𝄿 lh𝅘𝅥𝅯> l𝅘𝅥𝅯 𝄿 𝄿 hl♪ hl♪ lh♪ lh♪> |  ' # Took off my hat...
                 '  lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ lh♪> lh♪ | ', # Me, working for you
                 
            ),  
            bell_part(
                #                     And the
                '  𝄻 | 𝄻 |  𝄼 𝄽 𝄾 a𝅘𝅥𝅯 b𝅘𝅥𝅯 |'
                
                # sign says long-haired freaky people 
                '  c♩ c♩     b♪ b♪      b♪ b𝅘𝅥𝅯 G𝅘𝅥𝅯  |  '
                
                # (need) not a-       pply
                # need not apply  so I - 7/24
                ' 𝄾 a♪ a♪ 𝄿 G𝅘𝅥𝅯 𝄽 𝄾 a♪  |'

                # tucked my hair up under my hat and I -- 7/24
                '𝄿 a♪    𝄿 a♪   a♪  b♪ a♪ a♪ d𝅘𝅥𝅯 b𝅘𝅥𝅯 |'

                # went in to ask him why -- 7/24
                ' d♪      b♪ d♪ d♪   b𝅘𝅥𝅯 a𝅘𝅥𝅯 𝄾 𝄽 |'

                #   He said, you look like a fine, upstanding young -- 7/24
                '  𝄿 e𝅘𝅥𝅯 e𝅘𝅥𝅯   e𝅘𝅥𝅯  e𝅘𝅥𝅯   e𝅘𝅥𝅯   e♪  d♪   c♪ c♪     d♪ |'

                # man,  I think you'll do, uh, so I -- 7/24
                ' d𝅘𝅥𝅯 c♪ a𝅘𝅥𝅯 d♪ d♪       c♩  𝄿 a𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  |'

                # took off my hat and said imagine that, huh -- 7/24
                ' e𝅘𝅥𝅯   e♪  c𝅘𝅥𝅯 e♪      c♪   d♪   d♪    𝄿 e𝅘𝅥𝅯  𝄾 |'

                # me,   working for you,    Oh...
                '  c♪ 𝄾  c♪      c♪ d♪  𝄾  𝄾  G♪  '  # e♪ 𝄿 e𝅘𝅥𝅯 d𝅘𝅥𝅯 e𝅘𝅥𝅯 d♪ | ' -- 7/24
            ),
            sequence_part(
                '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  '
                '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  '
                '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩  ',
                sequence(
                    random_each,
                    measures=10,
                    special=ActionParams(action=dimmer_sequence_flip(1)),
                ),
                sequence(
                    blink_all,
                    special=DimmerParams(),
                ),
            ),
        )

    def refrain(self, play_thru: int):
        """Signs song refrain."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            sequence_part(
                # Sign, sign, everywhere a sign
                '  ♪ ♪ ♩  | 𝄻  | 𝄻  | 𝄻  | 𝄻 ',
                sequence(blink_all),
            ),
            bell_part(
                # Sign, sign, everywhere a sign -- Would be good to keep these 16ths if they are not too much 7/24
                '  e♩  e♩  d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  c♩ |  '
                # Blockin' out the scenery, breakin' my mind -- 7/24
                '  e♪      e♪      e𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪   a𝅘𝅥𝅯 c𝅘𝅥𝅯 c♪ c♩ |  '
                # Do this, don't do that,   can't you read   the   sign? -- Do the e 16ths need to be simplifed?
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 𝄿 e𝅘𝅥𝅯   𝄿 e𝅘𝅥𝅯 c𝅘𝅥𝅯 d𝅘𝅥𝅯    𝄿 de𝅘𝅥𝅯 de𝅘𝅥𝅯 de𝅘𝅥𝅯    𝄾 d𝅘𝅥𝅯 d𝅘𝅥𝅯  | '
                '  c♪ 𝄿 d𝅘𝅥𝅯 ' + (' 𝄽 𝄼 | ' if play_thru == 1 else ' 𝄽 𝄽 𝄾 c♪ | c♩ ')
            ),
            sequence_part(
                # Sign, sign, everywhere a sign
                '  𝄻  | 𝅝  | 𝅝  | 𝅝  | 𝅝 ',
                sequence(blink_all, on_first=False,
                    special=DimmerParams(
                        transition_off=3.5,
                        transition_on=3.5,
                    )
                ),
            ),
        )
 
    def transition (self):
        """Signs song transition."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drum_part(
            '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
            # '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
            # '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
            # '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
            # # '  lh♩ lh♩ lh♩ lh♩ | l♪ h♪ l♪ h♪ l♪ h♪ l♪ h♪|  '
            )
        )

    # '  D♪ D♪ D♪ D♪ |  ' Build-up experiment

    # '  𝄽 𝄽 eca♪ eca♪ eEG♪ eEG♪ |  ' Build-up experiment

            #drum_part(
            # for build-up    '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |  '
            #),
