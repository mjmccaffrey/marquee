"""Marquee Lighted Sign Project - christmas"""

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
            song.play(tempo=120)

    def jingle_bells(self) -> Section:
        """Jingle Bells."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            bell_part(
                #  Jingle Bells, Jingle Bells,
                '  b♩ b♩   b♩ 𝄽  | b♩ b♩   b♩ 𝄽  |'
                
                #  Jingle all the   way 
                '  b♩ d♩   G♩ 𝄾 a♪  | b♩ 𝄽 𝄽 𝄽   |'
                
                # Oh what fun it    is to ride in a 
                ' c♩ c♩   c♩ 𝄾 c♪ |  c♩ b♩ b♩    b♪ b♪ |'

                # one horse open  sleigh
                '  b♩ a♩   a♩ b♩   | a♩ 𝄽 d♩ 𝄽 |'

                #  Jingle Bells, Jingle Bells,
                '  b♩ b♩   b♩ 𝄽  | b♩ b♩   b♩ 𝄽  |'
                
                #  Jingle all the   way 
                '  b♩ d♩   G♩ 𝄾 a♪  | b♩ 𝄽 𝄽 𝄽   |'
                
                # Oh what fun it    is to ride in a 
                ' c♩ c♩   c♩ 𝄾 c♪ |  c♩ b♩ b♩    b♪ b♪ |'

                # one horse open  sleigh
                '  d♩ d♩    c♩ a♩ | G♩ 𝄽 𝄽 𝄽  |'
            ),
        )

    def jolly_old(self) -> Section:
        """Jolly Old St. Nicholas."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            bell_part(
                # Jolly   Old St.  Nicholas
                '  b♪ b♪   b♪ b♪ | a♪ a♪   a♩ |'
                
                # Lean your ear this way
                '  G♪ G♪   G♪ G♪   | b♩ 𝄽  |'

                # Don't you tell a single soul
                '  e♪ e♪   e♪ e♪   | D♪ D♪   G♩ |'
                
                # What I'm here to say
                '  G♪ G♪  a♪ b♪   | a♩ 𝄽 |' 
                # (Or replace the first G with F#)

                # Christmas Eve is coming soon
                '  b♪ b♪   b♪ b♪  | a♪ a♪   a♩ |'
                
                # Now you dear old man
                '  G♪ G♪   G♪ G♪   | b♩ 𝄽  |'

                # Whisper what you’ll bring to me
                '  e♪ e♪   e♪ e♪     | D♪ D♪   G♩ |'
                
                # Tell me if you    can
                '  a♪ G♪   a♪ b♪  | G♩ 𝄽           |'            ),
        )
    

    def deck_the_halls(self) -> Section:
        """Deck the Halls."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            bell_part(
                # Deck the halls with
                ' d♩ 𝄾 c♪ b♩ a♩ |'
                
                # Boughs of Holly
                ' G♩ a♩ b♩ G♩ |'

                # Fa la la la la, la 
                ' a♪ b♪ c♪ a♪ b♩ 𝄾 a♪ | ' 
                
                # la la la
                ' G♩ a♩ G♩ 𝄽 |'
                #Or replace the last a with F#
        )