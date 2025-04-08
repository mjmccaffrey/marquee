"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
import itertools
import time
from typing import Any

from instruments import Instrument, ActionInstrument, BellSet, DrumSet, RestInstrument
# from signs import ActionParams, SpecialParams
import signs
from modes import PlayMode

accent_symbols = '->^'
pitch_symbols = 'DEGAabcde'
note_duration: dict[str, float] = {
    '𝅝': 4,     '𝅗𝅥': 2,      '♩': 1,
    '♪': 0.5,   '𝅘𝅥𝅯': 0.25,  '𝅘𝅥𝅰': 0.125,
}
rest_duration: dict[str, float] = {
    '𝄻': 4,    '𝄼': 2,      '𝄽': 1,
    '𝄾': 0.5,   '𝄿': 0.25,  '𝅀': 0.125,
}
symbol_duration = note_duration | rest_duration

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
        self.bells = self.player.sign.bell_set
        self.drums = self.player.sign.drum_set
        # self.beat_unit = 1/4
        self.tempo = 60

    @property
    def tempo(self):
        return self._tempo
    
    @tempo.setter
    def tempo(self, value: float):
        self._tempo = value
        self.pace = 60 / self._tempo

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
        special: signs.SpecialParams | None = None,
    ):
        """Return callable to effect light pattern."""
        print("*********", pattern)
        if isinstance(special, signs.ActionParams):
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
        special: signs.SpecialParams | None = None,
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
                    PlayMusicMode.ActionNote(
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
                isinstance(e, PlayMusicMode.NoteBase)
                for e in measure.elements
            )
            for element in measure.elements:
                print("playing", element)
                start = time.time()
                assert isinstance(element, PlayMusicMode.NoteBase)
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
                        assert isinstance(element, PlayMusicMode.NoteBase)
                        beat_next[p] = beat + element.duration
                        print(element)
                        if not isinstance(element, PlayMusicMode.Rest):
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

    def interpret_symbols(self, symbols: str) -> tuple[float, str, str, "Rest | None"]:
        """Returns duration, pitch, accent, rest. """
        if not symbols:
            raise ValueError("Invalid (empty) symbol.")
        elif symbols.startswith('3'):
            duration, pitch, accent, rest = self.interpret_symbols(symbols[1:])
            duration *= 2/3
        elif symbols[-1] in accent_symbols:
            duration, pitch, _, rest = self.interpret_symbols(symbols[:-1])
            accent = symbols[-1]
        elif symbols[-1] in pitch_symbols:
            duration, _, _, rest = self.interpret_symbols(symbols[:-1])
            pitch = symbols[-1]
        else:
            if any(
                s not in symbol_duration for s in symbols
            ):
                raise ValueError("Invalid symbol.")
            if any(
                s in rest_duration and s in note_duration for s in symbols
            ):
                raise ValueError("Cannot mix note and rest symbols.")
            if symbols[0] in rest_duration:
                duration = 0
                rest = self.rest(symbols)
            else:
                duration = sum(
                    note_duration[s]
                    for s in symbols
                )
                rest = None
            pitch, accent = "", ""
        return duration, pitch, accent, rest

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
        
    class NoteBase(Element):
        """"""

        @abstractmethod
        def __init__(
            self, 
            mode: "PlayMusicMode",
            name: str,
            instrument_class: type[Instrument],
            duration: float,
        ):
            super().__init__(mode)
            self.name = name
            self.instrument_class = instrument_class
            self.duration = duration

        @abstractmethod
        def execute(self):
            """"""

    class ActionNote(NoteBase):
        """"""
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
            actions: tuple[Callable, ...],
        ):
            super().__init__(mode, "act", ActionInstrument, duration)
            assert actions, "Note must have at least 1 action."
            self.actions = actions

        def execute(self):
            for action in self.actions:
                action()

    def act(self, symbols: str, *actions: Callable) -> "ActionNote | Rest":
        duration, pitch, accent, rest = self.interpret_symbols(symbols)
        if pitch or accent:
            raise ValueError("Action note cannot have pitch or accent.")
        return rest or PlayMusicMode.ActionNote(self, duration, actions)

    class BellNote(NoteBase):
        """Bell Note"""
        def __init__(
            self, 
            mode: "PlayMusicMode",
            duration: float,
            #
            pitch: str,
        ):
            super().__init__(mode, 'bell', BellSet, duration)
            self.pitch = pitch

        def execute(self):
            raise NotImplementedError

    def bell(self, symbols: str) -> "BellNote | Rest":
        duration, pitch, accent, rest = self.interpret_symbols(symbols)
        if accent:
            raise ValueError("Bell note cannot have accent.")
        return rest or PlayMusicMode.BellNote(self, duration, pitch)

    def bell_part(self, notation: str, beats_per_measure=4) -> "PlayMusicMode.Part":
        return self.part(
            *self.notation(self.bell, notation, beats_per_measure)
        )

    class DrumNote(NoteBase):
        """Drum Note"""
        def __init__(
            self, 
            mode: "PlayMusicMode",
            duration: float,
            #
            accent: str,
        ):
            super().__init__(mode, 'bell', BellSet, duration)
            self.accent = accent

        def execute(self):
            raise NotImplementedError

    def drum(self, symbols: str) -> "DrumNote | Rest":
        duration, pitch, accent, rest = self.interpret_symbols(symbols)
        if pitch:
            raise ValueError("Drum note cannot have pitch.")
        return rest or PlayMusicMode.DrumNote(self, duration, accent)

    def drum_part(self, notation: str, beats_per_measure=4) -> "PlayMusicMode.Part":
        return self.part(
            *self.notation(self.drum, notation, beats_per_measure)
        )

    class Rest(NoteBase):
        """ Duration in Beats. """
        def __init__(
            self, 
            mode: "PlayMusicMode", 
            duration: float,
        ):
            super().__init__(mode, "rest", RestInstrument, duration)

        def execute(self):
            """"""

    def rest(self, symbols: str) -> Rest:
        duration, pitch, accent, rest = self.interpret_symbols(symbols)
        if pitch or accent:
            raise ValueError("Rest cannot have pitch or accent.")
        return rest or PlayMusicMode.Rest(self, duration)

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
        element_factory: Callable[[str], Element],
        notation: str, 
        beats_per_measure: int = 4,
    ) -> tuple[Measure, ...]:
        """"""
        def create_measure(measure):
            return PlayMusicMode.Measure(
                self,
                tuple(
                    element_factory(symbols)
                    for symbols in measure.split()
                ),
                beats = beats_per_measure,
            )
        return tuple(
            create_measure(measure)
            for measure in notation.split('|')
        )

    class Sequence(Element):
        """"""

        def __init__(
            self,
            mode: "PlayMusicMode", 
            step_duration: float, 
            count: int,
            sequence: Callable,
            special: signs.SpecialParams | None = None,
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
        special: signs.SpecialParams | None = None,
        **kwargs,
    ):
        step_duration, _, _, _ = self.interpret_symbols(symbols)
        return PlayMusicMode.Sequence(
            self, step_duration, count, sequence, special, **kwargs)
