"""Marquee Lighted Sign Project - signs_song"""

from modes import PlayMusicMode
from music import (
    set_player,
    act_part, bell_part, drum_part, sequence_part,
    dimmer_sequence_flip, section, Section, sequence,
)


class ChristmasSongs(PlayMusicMode):
    """Christmas songs."""

    def execute(self) -> None:
        """Perform Christmas songs."""
        # set_player(self.player)
        songs: list[Section] = [
            self.jingle_bells(),
        ]
        for song in songs:
            song.play(tempo=75)

    def jingle_bells(self) -> Section:
        """Jingle Bells."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            bell_part(
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
        )
