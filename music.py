"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
import itertools
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

    def light_seq(self, sequence=None):
        """"""
        if sequence is not None:
            self.sequence = itertools.cycle(sequence())
        return self.light(next(self.sequence))
    
    def relay(self, *indices):
        """Flip"""
        return lambda: self.player.sign.flip_extra_relays(*indices)
    
    def play_measures(self, *measures: "_Measure"):
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

    def play_parts(self, *parts: "_Part"):
        """"""
        assert parts
        measure_count = [len(p.measures) for p in parts]
        assert all(c == measure_count[0] for c in measure_count)

        measure_groups = zip(*(p.measures for p in parts))
        new_measures = [
            self.process_measure_group(parts, measure_group)
            for measure_group in measure_groups
        ]
        print(new_measures)
        self.play_measures(*new_measures)

    def process_measure_group(
        self, 
        parts: tuple["_Part", ...], 
        measure_group: tuple["_Measure", ...]
    ) -> "PlayMusicMode._Measure":
        print("PMG")
        beats = measure_group[0].beats
        assert all(m.beats == beats for m in measure_group)
        measure = {
            p: measure_group[i]
            for i, p in enumerate(parts)
        }
        elements_in = {p: iter(measure[p].elements) for p in parts}
        elements_out: list[PlayMusicMode._Element] = []
        beat_next: dict[PlayMusicMode._Part, float | None] = {p: 0 for p in parts}
        beat, next_beat = 0.0, 0.0
        while any(beat_next[p] is not None for p in parts):
            beat = next_beat
            for p in parts:
                out = []
                print(f"beat: {beat}, beat_next: {beat_next[p]}")
                if beat_next[p] == beat:
                    element = next(elements_in[p], None)
                    if element is None:
                        beat_next[p] = None
                    else:
                        beat_next[p] = beat + element.duration
                        print(element)
                        if isinstance(element, PlayMusicMode._Note):
                            out.append(element)
            if not all(beat_next[p] is None for p in parts):
                next_beat = min(
                    beat_next[p] for p in parts  # type: ignore
                    if beat_next[p] is not None
                )
                if not out:
                    out.append(
                        PlayMusicMode._Rest(self, next_beat - beat)
                    )
            print(out)
            elements_out.extend(out)
        print(elements_out)
        return PlayMusicMode._Measure(self, *elements_out, beats=beats)

    class _Element(ABC):
        """"""

        @abstractmethod
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
        ) -> None:
            super().__init__()
            self.mode = mode
            self.duration = duration

        def __str__(self):
            """"""
            return f"{type(self).__name__} {self.duration}"
        
        def __repr__(self):
            """"""
            return f"<{self}>"
        
        @abstractmethod
        def execute(self) -> float:
            """Perform action(s), and return # of beats transpired."""

    class _Note(_Element):
        """ """
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
            *actions: Callable
        ) -> None:
            super().__init__(mode, duration)
            assert actions, "Note must have at least 1 action."
            self.actions = actions

        def execute(self) -> float:
            for action in self.actions:
                action()
            return self.duration

    def Note(self, symbols: str, *actions: Callable) -> _Note:
        duration = sum(
            symbol_duration[s]
            for s in symbols
        )
        return PlayMusicMode._Note(self, duration, *actions)

    class _Rest(_Element):
        """ Duration in Beats. """
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
        ) -> None:
            super().__init__(mode, duration)

        def execute(self):
            return self.duration

    def Rest(self, symbols: str) -> _Rest:
        duration = sum(
            symbol_duration[s]
            for s in symbols
        )
        return PlayMusicMode._Rest(self, duration)

    class _Sequence(_Element):
        """"""

        def __init__(
            self,
            mode: "PlayMusicMode", 
            duration: float, 
            count: int,
            sequence: Callable,
            specialparams: SpecialParams | None = None,
            **kwargs,
        ) -> None:
            super().__init__(mode, duration)
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
        duration = sum(
            symbol_duration[s]
            for s in symbols
        )
        return PlayMusicMode._Sequence(
            self, duration, count, sequence, specialparams, **kwargs)
    
    class _Measure(_Element):
        """"""

        def __init__(
            self, 
            mode: "PlayMusicMode", 
            *elements: "PlayMusicMode._Element",
            beats: int = 4,
        ) -> None:
            """"""
            super().__init__(mode, 0)
            self.elements = elements
            self.beats = beats

        def execute(self):
            return self.duration

    def Measure(self, *elements: "PlayMusicMode._Element", beats: int = 4) -> _Measure:
        return PlayMusicMode._Measure(self, *elements, beats=beats)

    class _Part(_Element):
        """"""

        def __init__(
            self, 
            mode: "PlayMusicMode", 
            *measures: "PlayMusicMode._Measure",
        ) -> None:
            """"""
            super().__init__(mode, 0)
            self.measures = measures

        def execute(self):
            return self.duration

    def Part(self, *measures: "PlayMusicMode._Measure") -> _Part:
        return PlayMusicMode._Part(self, *measures)
