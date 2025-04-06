"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import itertools
import time
from typing import Any, Self

from signs import ActionParams, SpecialParams
from modes import PlayMode

symbol_duration: dict[str, float] = {
    '𝅝': 4,     '𝄻': 4,
    '𝅗𝅥': 2,     '𝄼': 2,
    '♩': 1,     '𝄽': 1,
    '♪': 0.5,   '𝄾': 0.5,
    '𝅘𝅥𝅯': 0.25,  '𝄿': 0.25,
    '𝅘𝅥𝅰': 0.125, '𝅀': 0.125,
}
ACCENT_SYMBOLS = "->^"
symbol_accent_level: dict[str, int] = {
    '-': 4, '>': 6, '^': 8,
}
TONE_SYMBOLS = "DEGAabcde"
symbol_pitch_level: dict[str, int] = {
    p: l for l, p in enumerate(TONE_SYMBOLS)
}

class PlayMusicMode(PlayMode):
    """4 beats per measure by default.
       Every quarter note gets a beat."""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        #
    ):
        super().__init__(player, name, preset_dimmers=True)
        # self.beat_unit = 1/4
        self.tempo = 60
        self.bells = PlayMusicMode.bell
        self.clicks = PlayMusicMode.click

    @property
    def tempo(self):
        return self._tempo
    
    @tempo.setter
    def tempo(self, value: float):
        self._tempo = value
        self.pace = 60 / self._tempo

    @staticmethod
    def interpret_symbols(symbols: str) -> tuple[float, int | None, int]:
        """Returns duration, pitch, accent. """
        if not symbols:
            raise ValueError("Invalid (empty) symbol.")
        elif symbols.startswith('3'):
            duration, pitch, accent = PlayMusicMode.interpret_symbols(symbols[1:])
            duration *= 2/3
        elif symbols[-1] in ACCENT_SYMBOLS:
            duration, pitch, _ = PlayMusicMode.interpret_symbols(symbols[:-1])
            accent = symbol_accent_level[symbols[-1]]
        elif symbols[-1] in TONE_SYMBOLS:
            duration, _, _ = PlayMusicMode.interpret_symbols(symbols[:-1])
            pitch = symbol_pitch_level[symbols[-1]]
        else:
            duration = sum(
                symbol_duration[s]
                for s in symbols
            )
            pitch = None
            accent = 0
        return duration, pitch, accent

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
            self.current_sequence = itertools.cycle(sequence(**kwargs))
            self.current_special = special
        return self.light(
            pattern=next(self.current_sequence),
            special=self.current_special,
        )
    
    def relay(self, *indices):
        """Flip"""
        return lambda: self.player.sign.flip_extra_relays(*indices)
    
    def expand_sequences(self, measures: tuple["Measure", ...]):
        """"""
        for measure in measures:
            if not measure.elements:
                continue
            if isinstance(measure.elements[0], PlayMusicMode.Sequence):
                print("sequence found.")
                assert len(measure.elements) == 1, \
                    "Sequence must be the only element in the measure."
                seq = measure.elements[0]
                measure.elements = tuple(
                    PlayMusicMode.Note(
                        mode=self,
                        duration=seq.step_duration,
                        actions=(
                            self.light_seq(
                                sequence=seq.sequence, 
                                special=seq.special,
                                **seq.kwargs,
                            )
                                if c == 0 else 
                            self.light_seq(),
                        ),
                    )
                    for c in range(seq.count)
                )

    def play_measures(self, *measures: "Measure"):
        """"""
        for measure in measures:
            print("PLAYING MEASURE")
            beat = 0
            self.expand_sequences(measures)
            assert all(
                isinstance(e, PlayMusicMode.PlayableElement)
                for e in measure.elements
            )
            for element in measure.elements:
                print("playing", element)
                assert isinstance(element, PlayMusicMode.PlayableElement)
                if isinstance(element, PlayMusicMode.Note):
                    start = time.time()
                    element.execute()
                    wait = (element.duration) * self.pace
                    self.player.wait(wait, elapsed = time.time() - start)
                beat += element.duration
                # print(f"beat is now {beat}")
            wait = max(0, measure.beats - beat) * self.pace
            self.player.wait(wait)

    def play_parts(self, *parts: "Part"):
        """"""
        assert parts
        measure_count = [len(p.measures) for p in parts]
        assert all(c == measure_count[0] for c in measure_count)
        for part in parts:
            self.expand_sequences(part.measures)
        measure_groups = zip(*(p.measures for p in parts))
        new_measures = [
            self.process_measure_group(parts, measure_group)
            for measure_group in measure_groups
        ]
        #print(new_measures)
        self.play_measures(*new_measures)

    def process_measure_group(
        self, 
        parts: tuple["Part", ...], 
        measure_group: tuple["Measure", ...],
    ) -> "PlayMusicMode.Measure":
        beats = measure_group[0].beats
        assert all(m.beats == beats for m in measure_group)
        measure = {
            p: measure_group[i]
            for i, p in enumerate(parts)
        }
        elements_in = {p: iter(measure[p].elements) for p in parts}
        elements_out: list[PlayMusicMode.Element] = []
        beat_next: dict[PlayMusicMode.Part, float | None] = {p: 0 for p in parts}
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
                        assert isinstance(element, PlayMusicMode.PlayableElement)
                        beat_next[p] = beat + element.duration
                        print(element)
                        if isinstance(element, PlayMusicMode.Note):
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
                        PlayMusicMode.Rest(self, next_beat - beat)
                    )
            print(out)
            elements_out.extend(out)
        print(elements_out)
        return PlayMusicMode.Measure(self, tuple(elements_out), beats=beats)

    class Element(ABC):
        """"""
        @abstractmethod
        def __init__(
            self, 
            mode: "PlayMusicMode", 
        ):
            super().__init__()
            self.mode = mode

        def __str__(self):
            return f"{type(self).__name__}"
        
        def __repr__(self):
            return f"<{self}>"
        
    class PlayableElement(Element):
        """"""
        @abstractmethod
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
        ):
            super().__init__(mode)
            self.duration = duration

        def __str__(self):
            return f"{type(self).__name__}"
        
        def __repr__(self):
            return f"<{self}>"
        
    class Note(PlayableElement):
        """Generic note"""
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
            actions: tuple[Callable, ...],
        ):
            super().__init__(mode, duration)
            assert actions, "Note must have at least 1 action."
            self.actions = actions

        def execute(self):
            for action in self.actions:
                action()

    def note(self, symbols: str, *actions: Callable) -> Note:
        duration, pitch, accent = PlayMusicMode.interpret_symbols(symbols)
        if pitch or accent:
            raise ValueError("Generic note cannot have pitch or accent.")
        return PlayMusicMode.Note(self, duration, actions)

    class Bell(PlayableElement):
        """Bell Note"""
        def __init__(
            self, 
            mode: "PlayMusicMode",
            duration: float,
            #
            pitch: int | None,
        ):
            super().__init__(mode, duration)
            self.pitch = pitch

        def execute(self):
            raise NotImplementedError

    def bell(self, symbols: str) -> Bell:
        duration, pitch, accent = PlayMusicMode.interpret_symbols(symbols)
        if pitch is None:
            raise ValueError("Bell must have pitch.")
        if accent:
            raise ValueError("Bell cannot have accent.")
        return PlayMusicMode.Bell(self, duration, pitch)

    class Click(PlayableElement):
        """Click Note"""
        def __init__(
            self, 
            mode: "PlayMusicMode",
            duration: float,
            #
            accent: int,
        ):
            super().__init__(mode, duration)
            self.accent = accent

        def execute(self):
            raise NotImplementedError

    def click(self, symbols: str) -> Click:
        duration, pitch, accent = PlayMusicMode.interpret_symbols(symbols)
        if pitch:
            raise ValueError("Click cannot have pitch.")
        return PlayMusicMode.Click(self, duration, accent)

    class Rest(PlayableElement):
        """ Duration in Beats. """
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
        ):
            super().__init__(mode, duration)

    def rest(self, symbols: str) -> Rest:
        duration, pitch, accent = PlayMusicMode.interpret_symbols(symbols)
        if pitch or accent:
            raise ValueError("rest cannot have pitch or accent.")
        return PlayMusicMode.Rest(self, duration)

    class Part(Element):
        """"""

        def __init__(
            self, 
            mode: "PlayMusicMode", 
            measures: tuple["PlayMusicMode.Measure", ...],
        ):
            """"""
            super().__init__(mode)
            self.measures = measures

    def part(self, *measures: "PlayMusicMode.Measure") -> Part:
        return PlayMusicMode.Part(self, measures)

    class Measure(Element):
        """"""

        def __init__(
            self, 
            mode: "PlayMusicMode", 
            elements: tuple["PlayMusicMode.Element", ...],
            beats: int = 4,
        ):
            """"""
            super().__init__(mode)
            self.elements = elements
            self.beats = beats

    def measure(self, *elements: "PlayMusicMode.Element", beats: int = 4) -> Measure:
        return PlayMusicMode.Measure(self, elements, beats=beats)

    def notation(
        self, 
        element_factory: Callable[[Self, str], Element],
        notation: str, 
        beats_per_measure: int = 4,
    ) -> tuple[Measure, ...]:
        """"""
        def create_measure(measure):
            return PlayMusicMode.Measure(
                self,
                tuple(
                    element_factory(self, symbols)
                    for symbols in measure.split()
                ),
                beats = beats_per_measure,
            )
        return tuple(
            create_measure(measure)
            for measure in notation.split('|')
        )

    def bell_part(self, notation: str, beats_per_measure: int = 4): 
        return self.part(
            *self.notation(PlayMusicMode.bell, notation, beats_per_measure)
        )

    def click_part(self, notation: str, beats_per_measure: int = 4): 
        return self.part(
            *self.notation(PlayMusicMode.click, notation, beats_per_measure)
        )

    class Sequence(Element):
        """"""

        def __init__(
            self,
            mode: "PlayMusicMode", 
            step_duration: float, 
            count: int,
            sequence: Callable,
            special: SpecialParams | None = None,
            **kwargs,
        ):
            super().__init__(mode)
            self.step_duration = step_duration
            self.count = count
            self.sequence = sequence
            self.special = special
            self.kwargs = kwargs

    def sequence(
        self,
        symbols: str,
        count: int,
        sequence: Callable,
        special: SpecialParams | None = None,
        **kwargs,
    ):
        step_duration, _, _ = PlayMusicMode.interpret_symbols(symbols)
        return PlayMusicMode.Sequence(
            self, step_duration, count, sequence, special, **kwargs)
