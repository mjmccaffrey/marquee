"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
import time
from typing import Any

from signs import Sign, SpecialParams
from modes import PlayMode, PlaySequenceMode, DimmerParams

symbol_duration: dict[str, float] = {
    '𝅝': 4,     '𝄻': 4,
    '𝅗𝅥': 2,     '𝄼': 2,
    '♩': 1,     '𝄽': 1,
    '♪': 0.5,   '𝄾': 0.5,
    '𝅘𝅥𝅯': 0.25,  '𝄿': 0.25,
    '𝅘𝅥𝅰': 0.125, '𝅀': 0.125,
}

class PlayMusicMode(PlayMode):
    """"""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        #
    ):
        super().__init__(player, name)
        tempo = 100
        self.pace = 60 / tempo
        self.beat_unit = 1/4

    def dimmer_seq(self, brightness: int, transition: float):
        """Return callable to effect state of specified dimmers."""
        return lambda lights: self.player.sign.execute_dimmer_commands(
            [
                (self.player.sign.dimmer_channels[l], brightness, transition)
                for l in lights
            ]
        )

    def dimmer(self, pattern: str):
        """"""
        return lambda: self.player.sign.set_dimmers(pattern)

    def light(self, pattern: str):
        """Return callable to effect light pattern."""
        return lambda: self.player.sign.set_lights(pattern)

    def relay(self, *indices):
        """Flip"""
        return lambda: self.player.sign.flip_extra_relays(*indices)
    
    def play(self, *measures: "_Measure"):
        """"""
        for measure in measures:
            beat = 0
            for element in measure.elements:
                start = time.time()
                beats_elapsed = element.execute()
                wait = (beats_elapsed) * self.pace
                self.player.wait(wait, elapsed = time.time() - start)
                beat += beats_elapsed
                # print(f"beat is now {beat}")
            wait = max(0, measure.beats - beat) * self.pace
            self.player.wait(wait)

    class _Element(ABC):
        """"""

        @abstractmethod
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            symbols: str,
        ) -> None:
            super().__init__()
            self.mode = mode
            self.duration = sum(
                symbol_duration[s]
                for s in symbols
            )

        @abstractmethod
        def execute(self) -> float:
            """Perform action(s), and return # of beats transpired."""

    class _Note(_Element):
        """ """
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            symbols: str,
            *actions: Callable
        ) -> None:
            super().__init__(mode, symbols)
            assert actions, "Note must have at least 1 action."
            self.actions = actions

        def execute(self) -> float:
            for action in self.actions:
                action()
            return self.duration

    def Note(self, symbols: str, *actions: Callable) -> _Note:
        return PlayMusicMode._Note(self, symbols, *actions)

    class _Rest(_Element):
        """ Duration in Beats. """
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            symbols: str,
        ) -> None:
            super().__init__(mode, symbols)

        def execute(self):
            return self.duration

    def Rest(self, symbols: str) -> _Rest:
        return PlayMusicMode._Rest(self, symbols)

    class _Sequence(_Element):
        """"""

        def __init__(
            self,
            mode: "PlayMusicMode", 
            symbols: str,
            count: int,
            sequence: Callable,
            specialparams: SpecialParams | None = None,
            **kwargs,
        ) -> None:
            super().__init__(mode, symbols)
            self.duration *= count
            self.count = count
            self.mode = PlaySequenceMode(
                mode.player,
                "Music Sequence",
                sequence,
                mode.pace,
                count,
                specialparams,
                is_primary=False,
                **kwargs,
            )

        def execute(self):
            self.mode.play_sequence_once()
            return self.duration

    def Sequence(
        self,
        symbols: str,
        count: int,
        sequence: Callable,
        specialparams: SpecialParams | None = None,
        **kwargs,
    ):
        return PlayMusicMode._Sequence(
            self, symbols, count, sequence, specialparams, **kwargs)
    
    class _Measure(_Element):
        """"""

        def __init__(
            self, 
            mode: "PlayMusicMode", 
            *elements: "PlayMusicMode._Element",
            beats: int = 4,
        ) -> None:
            """"""
            super().__init__(mode, '')
            self.elements = elements
            self.beats = beats

        def execute(self):
            return self.duration

    def Measure(self, *elements: "PlayMusicMode._Element", beats: int = 4) -> _Measure:
        return PlayMusicMode._Measure(self, *elements, beats=beats)
