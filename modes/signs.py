"""Marquee Lighted Sign Project - signs"""

from typing_extensions import override

from device_defs import ALL_OFF, ALL_ON
from . import MusicMode
from .sequences import all_on, blink_all, random_each
from music import (
    actions, bells, drums, sequences,
    dimmer_sequence_flip, piece, section, Section, sequence,
)
from devices.specialparams import ActionParams, ChannelParams


class Signs(MusicMode):
    """Signs song."""

    @override
    def execute(self) -> None:
        """Perform Signs song."""
        self.lights.set_channels(brightness=0, force=True)
        # time.sleep(0.75) !!!
        self.lights.set_relays(ALL_ON)
        piece(
            self.intro(),
            # self.refrain(1),
            self.transition(),
            # self.refrain(2),
        ).play(tempo=int(75 * self.speed_factor))

    def intro(self) -> Section:
        """Signs song intro."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
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
            # bells(
            #     #                     And the
            #     '  𝄻 | 𝄻 |  𝄼 𝄽 𝄾 a𝅘𝅥𝅯 b𝅘𝅥𝅯 |'
                
            #     # sign says long-haired freaky people 
            #     '  c♩ c♩     b♪ b♪      b♪ b𝅘𝅥𝅯 G𝅘𝅥𝅯  |  '
                
            #     # need not apply  so I
            #     ' 𝄾 a♪ a♪ 𝄿 G𝅘𝅥𝅯 𝄽 𝄾 a♪  |'

            #     # tucked my hair up under my hat and I
            #     '𝄿 a♪    𝄿 a♪   a♪  b♪ a♪ a♪ d𝅘𝅥𝅯 b𝅘𝅥𝅯 |'

            #     # went in to ask him why
            #     ' d♪      b♪ d♪ d♪   b𝅘𝅥𝅯 a𝅘𝅥𝅯 𝄾 𝄽 |'

            #     #   He said, you look like a fine, upstanding young 
            #     '  𝄿 e𝅘𝅥𝅯 e𝅘𝅥𝅯   e𝅘𝅥𝅯  e𝅘𝅥𝅯   e𝅘𝅥𝅯   e♪  d♪   c♪ c♪     d♪ |'

            #     # man,  I think you'll do, uh, so I
            #     ' d𝅘𝅥𝅯 c♪ a𝅘𝅥𝅯 d♪ d♪       c♩  𝄿 a𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  |'

            #     # took off my hat and said imagine that, huh
            #     ' e𝅘𝅥𝅯   e♪  c𝅘𝅥𝅯 e♪      c♪   d♪   d♪    𝄿 e𝅘𝅥𝅯  𝄾 |'

            #     # me,   working for you,    Oh...
            #     '  c♪ 𝄾  c♪      c♪ d♪  𝄾  𝄾  G♪  '  # e♪ 𝄿 e𝅘𝅥𝅯 d𝅘𝅥𝅯 e𝅘𝅥𝅯 d♪ | '
            # ),
            # sequences(
            #     '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  '
            #     '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  '
            #     '  ♩ ♩ ♩ ♩  |  ♩ ♩ ♩ ♩  |  ',
            #     sequence(
            #         random_each,
            #         measures=10,
            #         special=ActionParams(action=dimmer_sequence_flip(transition=1.0)),
            #     ),
            # ),
            # actions(
            #         '  𝄻  |  ' * 10 + '  ♩ ♩  |  ',
            #         lambda: self.lights.set_relays(ALL_OFF),
            #         lambda: self.lights.set_relays(ALL_ON, special=ChannelParams()),
            # ),
        )

    def refrain(self, play_thru: int) -> Section:
        """Signs song refrain."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            # bells(
            #     # Sign, sign, everywhere a sign
            #     '  e♩  e♩  d𝅘𝅥𝅯 c𝅘𝅥𝅯 c𝅘𝅥𝅯 a𝅘𝅥𝅯  c♩ |  '
            #     # Blockin' out the scenery, breakin' my mind
            #     '  e♪      e♪      e𝅘𝅥𝅯 d𝅘𝅥𝅯 c♪   a𝅘𝅥𝅯 c𝅘𝅥𝅯 c♪ c♩ |  '
            #     # Do this, don't do that,   can't you read   the   sign?
            #     '  e𝅘𝅥𝅯 e𝅘𝅥𝅯 𝄿 e𝅘𝅥𝅯   𝄿 e𝅘𝅥𝅯 c𝅘𝅥𝅯 d𝅘𝅥𝅯    𝄿 de𝅘𝅥𝅯 de𝅘𝅥𝅯 de𝅘𝅥𝅯    𝄾 d♪  | '
            #     '  c♪ 𝄿 d𝅘𝅥𝅯 ' + (' 𝄽 𝄼 | ' if play_thru == 1 else ' 𝄽 𝄽 𝄾 c♪ | c♩ ')
            # ),
            # sequences(
            #     # Sign, sign, everywhere a sign
            #     '  ♪ ♪ ♩  | 𝅝  | 𝅝  | 𝅝  | ',
            #     sequence(blink_all),
            #     sequence(blink_all, on_first=False,
            #         special=ChannelParams(
            #             trans_off=3.5,
            #             trans_on=3.5,
            #         )
            #     ),
            # ),
        )
 
    def transition (self) -> Section:
        """Signs song transition."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
            '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
            '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
            '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
            '  h𝅘𝅥𝅯 l𝅘𝅥𝅯 h𝅘𝅥𝅯 l𝅘𝅥𝅯   h𝅘𝅥𝅯- l𝅘𝅥𝅯- h𝅘𝅥𝅯- l𝅘𝅥𝅯-   h𝅘𝅥𝅯> l𝅘𝅥𝅯> h𝅘𝅥𝅯> l𝅘𝅥𝅯>   h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ h𝅘𝅥𝅯^ l𝅘𝅥𝅯^ |'
            '  lh♩ lh♩ lh♩ lh♩ | l♪ h♪ l♪ h♪ l♪ h♪ l♪ h♪|  '
            ),
            # sequences(
            #     '  𝅝  ',
            #     sequence(
            #         all_on,
            #         special=ChannelParams(trans_on=3.5),
            #     ),
            # ),
        )

