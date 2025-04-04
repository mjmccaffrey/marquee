"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
import itertools
import time
from typing import Any

from signs import Sign, ActionParams, SpecialParams
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
        super().__init__(player, name, preset_dimmers=True)  # !!!!!!!!!!
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

    def light(
        self, 
        pattern: Any,
        special: SpecialParams | None = None,
    ):
        """Return callable to effect light pattern."""
        print("*********", pattern)
        if isinstance(special, ActionParams):
            result = lambda: special.action(pattern)
        else:
            result = lambda: self.player.sign.set_lights(
                light_pattern=pattern,
                special=special,
            )
        return result

    def light_seq(
        self, 
        sequence=None, 
        special: SpecialParams | None = None,
        **kwargs,
    ):
        """"""
        if sequence is not None:
            self.sequence = itertools.cycle(sequence(**kwargs))
            self.special = special
        return self.light(
            pattern=next(self.sequence),
            special=self.special,
        )
    
    def relay(self, *indices):
        """Flip"""
        return lambda: self.player.sign.flip_extra_relays(*indices)
    
    def convert_sequences(self, part: "_Part"):
        """Sequence must be the only element in the measure."""
        for measure in part.measures:
            if not measure.elements:
                continue
            if isinstance(measure.elements[0], PlayMusicMode._Sequence):
                seq = measure.elements[0]
                for c in range(seq.count):
                    measure.elements = (
                        PlayMusicMode._Note(
                            mode=self,
                            duration=seq.duration,
                            actions=(
                                self.light_seq(
                                    sequence=seq.sequence, 
                                    special=seq.special,
                                    **seq.kwargs,
                                )
                                    if c == 0 else 
                                self.light_seq(),
                            ),
                        ),
                    )

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
        for part in parts:
            self.convert_sequences(part)
        measure_groups = zip(*(p.measures for p in parts))
        new_measures = [
            self.process_measure_group(parts, measure_group)
            for measure_group in measure_groups
        ]
        #print(new_measures)
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
            out = []
            for i, p in enumerate(parts):
                print(f"part: {i}, beat: {beat}, beat_next: {beat_next[p]}")
                if beat_next[p] == beat:
                    element = next(elements_in[p], None)
                    if element is None:
                        print(f"part: {i} OUT OF ELEMENTS")
                        beat_next[p] = None
                    else:
                        beat_next[p] = beat + element.duration
                        print(element)
                        if isinstance(element, PlayMusicMode._Note):
                            print("is a note")
                            out.append(element)
                        print(out)
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
        return PlayMusicMode._Measure(self, tuple(elements_out), beats=beats)

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
            actions: tuple[Callable, ...],
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
        return PlayMusicMode._Note(self, duration, actions)

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
            special: SpecialParams | None = None,
            **kwargs,
        ) -> None:
            super().__init__(mode, duration)
            self.duration *= count
            self.count = count
            self.sequence = sequence
            self.special = special
            self.kwargs = kwargs

        def execute(self):
            return self.duration

    def Sequence(
        self,
        symbols: str,
        count: int,
        sequence: Callable,
        special: SpecialParams | None = None,
        **kwargs,
    ):
        duration = sum(
            symbol_duration[s]
            for s in symbols
        )
        return PlayMusicMode._Sequence(
            self, duration, count, sequence, special, **kwargs)
    
    class _Measure(_Element):
        """"""

        def __init__(
            self, 
            mode: "PlayMusicMode", 
            elements: tuple["PlayMusicMode._Element", ...],
            beats: int = 4,
        ) -> None:
            """"""
            super().__init__(mode, 0)
            self.elements = elements
            self.beats = beats

        def execute(self):
            return self.duration

    def Measure(self, *elements: "PlayMusicMode._Element", beats: int = 4) -> _Measure:
        return PlayMusicMode._Measure(self, elements, beats=beats)

    class _Part(_Element):
        """"""

        def __init__(
            self, 
            mode: "PlayMusicMode", 
            measures: tuple["PlayMusicMode._Measure", ...],
        ) -> None:
            """"""
            super().__init__(mode, 0)
            self.measures = measures

        def execute(self):
            return self.duration

    def Part(self, *measures: "PlayMusicMode._Measure") -> _Part:
        return PlayMusicMode._Part(self, measures)
