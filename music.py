
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
import time
from typing import Any

from signs import Sign
from modes import PlayMode, PlaySequenceMode, RelayOverride

HIGH = 100

_1, __1 =   '𝅝', '𝄻'
_2, __2 =   '𝅗𝅥', '𝄼'
_4, __4 =   '♩', '𝄽'
_8, __8 =   '♪', '𝄾'
_16, __16 = '𝅘𝅥𝅯', '𝄿'

note_duration: dict[str, float] = {
     _1: 4,    __1: 4,
     _2: 2,    __2: 2,
     _4: 1,    __4: 1,
     _8: 0.5,  __8: 0.5,
    _16: 0.25, __16: 0.25,
}

class PlayMusicMode(PlayMode):
    """"""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        #
        tempo: int,
    ):
        print(1)
        super().__init__(player, name)
        print(2)
        self.pace = 60 / tempo
        self.beat_unit = 1/4

#    def dimmer(self, brightness: int, transition: float, *lights: int):
#        """Return callable to effect state of specified dimmers."""
#        return lambda: self.mode.sign.execute_dimmer_commands(
#            [
#                (s.dimmer_channels[l], brightness, transition)
#                for l in lights
#            ]
#        )

    def light(self, pattern: str):
        """Return callable to effect light pattern."""
        return lambda: self.player.sign.set_lights(pattern)
    
    def play(self, *measures: "_Measure"):
        """"""
        for measure in measures:
            beat = 0
            print(f"playing measure {measure.id}")
            for element in measure.elements:
                start = time.time()
                beats_elapsed = element.execute()
                wait = (beats_elapsed) * self.pace
                self.player.wait(wait, elapsed = time.time() - start)
                beat += beats_elapsed
                print(f"beat is now {beat}")
            wait = max(0, measure.beats - beat) * self.pace
            self.player.wait(wait)

    class _Element(ABC):
        """"""
        count: int = 0

        @abstractmethod
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
        ) -> None:
            super().__init__()
            self.id = PlayMusicMode._Element.count
            PlayMusicMode._Element.count += 1
            self.mode = mode
            self.duration = duration

        @abstractmethod
        def execute(self) -> float:
            """Perform action(s), and return # of beats transpired."""

    class _Note(_Element):
        """ """
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            note: str, *actions: Callable
        ) -> None:
            assert note in note_duration, "Invalid note."
            super().__init__(mode, note_duration[note])
            assert actions, "Note must have at least 1 action."
            self.actions = actions

        def execute(self) -> float:
            print(f"executing Note with {len(self.actions)} actions")
            for action in self.actions:
                action()
            return self.duration

    def Note(self, note: str, *actions: Callable) -> _Note:
        return PlayMusicMode._Note(self, note, *actions)

    class _Rest(_Element):
        """ Duration in Beats. """
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            note: str,
        ) -> None:
            assert note in note_duration, "Invalid note."
            super().__init__(mode, note_duration[note])

        def execute(self):
            return self.duration

    def Rest(self, note:str) -> _Rest:
        return PlayMusicMode._Rest(self, note)

    class _Sequence(_Element):
        """"""

        def __init__(
            self,
            mode: "PlayMusicMode", 
            note: str,
            count: int,
            sequence: Callable,
            override: RelayOverride | None = None,
            **kwargs,
        ) -> None:
            super().__init__(mode, note_duration[note] * count)
            self.count = count
            self.mode = PlaySequenceMode(
                mode.player,
                "Music Sequence",
                sequence,
                mode.pace,
                count,
                override,
                **kwargs,
            )
            print("sequence initialized")

        def execute(self):
            print("executing sequence")
            self.mode.play_sequence_once()
            return self.duration

    def Sequence(
        self,
        note: str,
        count: int,
        sequence: Callable,
        override: RelayOverride | None = None,
        **kwargs,
    ):
        return PlayMusicMode._Sequence(self, note, count, sequence)
    
    class _Measure(_Element):
        """"""

        all_measures: list["PlayMusicMode._Measure"] = []

        def __init__(
            self, 
            mode: "PlayMusicMode", 
            *elements: "PlayMusicMode._Element",
            beats: int = 4,
        ) -> None:
            """"""
            super().__init__(mode, 0)
            self.id = len(PlayMusicMode._Measure.all_measures)
            print(f"m: {self.id}")
            PlayMusicMode._Measure.all_measures.append(self)
            self.elements = elements
            self.beats = beats

        def execute(self):
            return self.duration

    def Measure(self, *elements: "PlayMusicMode._Element") -> _Measure:
        return PlayMusicMode._Measure(self, *elements)
