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
from sequences import all_off, all_on, blink_all, random_each
from definitions import ActionParams, DimmerParams, SpecialParams

class SignsSong(PlayMusicMode):
    """Signs song."""

    def execute(self):
        """Perform Signs song."""
        self.player.lights.set_dimmers(ALL_LOW, force_update=True)
        time.sleep(0.75)
        self.player.lights.set_relays(ALL_ON)
        sections = [
            self.intro(),
            self.refrain(1),
            self.transition(),
            self.refrain(2),
        ]
        for section in sections:
            section.play(tempo=75)
        self.player.wait(None)

    def intro_end_lights(self):
        count = 0
        def func(pattern):
            nonlocal count
            print(count)
            if count == 0:
                self.player.lights.set_relays(ALL_OFF)
            else:
                self.player.lights.set_relays(ALL_ON, special=DimmerParams())
            count += 1
        return func
    
    def intro(self):
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
                '  𝄻 | 𝄻 |  𝄼 𝄽 𝄾 a𝅘𝅥𝅯 b𝅘𝅥𝅯 |  '
                '  c♩ c♩     b♪ b♪      b♪ b𝅘𝅥𝅯 G𝅘𝅥𝅯  |  '
                '  𝄾 a♪ a♪ 𝄿 G𝅘𝅥𝅯 𝄽 𝄾 a♪  |  '
                '  𝄿 a♪  𝄿 a♪   a♪  b♪ a♪ a♪ d𝅘𝅥𝅯 b𝅘𝅥𝅯  |  '                 ),
            sequence_part(
                '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  '
                '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  '
                '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩  ',
                sequence(
                    random_each,
                    special=ActionParams(dimmer_sequence_flip(1)),
                ),
                sequence(
                    random_each,
                    special=ActionParams(self.intro_end_lights())
                ),
            ),
        )

    def refrain(self, play_thru: int):
        """Signs song refrain."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            sequence_part(
                # Sign, sign, everywhere a sign
                '  ♪ ♪ ♩  | 𝄻  | 𝄻  | 𝄻  | ',
                sequence(blink_all),
            ),
            bell_part(
                # Sign, sign, everywhere a sign
                '  e♩  e♩  d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  c♩ |  '
                # Blockin' out the scenery, breakin' my mind
                '  e♪      e♪      e𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪   a𝅘𝅥𝅯 c𝅘𝅥𝅯 c♪ c♩ |  '
                # Do this, don't do that,   can't you read   the   sign?
                '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 𝄿 e𝅘𝅥𝅯   𝄿 e𝅘𝅥𝅯 c𝅘𝅥𝅯 d𝅘𝅥𝅯    𝄿 de𝅘𝅥𝅯 de𝅘𝅥𝅯 de𝅘𝅥𝅯    𝄾 d♪  | '
                '  c♪ 𝄿 d𝅘𝅥𝅯 ' + (' 𝄽 𝄼 | ' if play_thru == 1 else ' 𝄽 𝄽 𝄾 c♪ | c♩ ')
            ),
            sequence_part(
                # Sign, sign, everywhere a sign
                '  𝄻  | 𝅝  | 𝅝  | 𝅝  | ',
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
            ),
            sequence_part(
                '  𝅝  ',
                sequence(
                    all_on,
                    special=DimmerParams(transition_on=3.5),
                ),
            ),
        )
