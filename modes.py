"""Marquee Lighted Sign Project - modes"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import itertools
import time
from typing import Any

from buttons import Button
from dimmers import TRANSITION_DEFAULT
from music import (
    Element, BaseNote, Rest, ActionNote, BellNote, DrumNote, Part, Measure,
    interpret_notation, interpret_symbols, merge_concurrent_measures,
)
from sequence_defs import seq_rotate_build_flip
from signs import ALL_HIGH, ALL_OFF, ALL_ON
from signs import ActionParams, DimmerParams, SpecialParams

@dataclass
class ModeConstructor:
    name: str
    mode_class: type["Mode"]
    kwargs: dict[str, Any]

class Mode(ABC):
    """Base for all Playing modes and the Select mode."""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        """"""
        self.player = player
        self.name = name
        if preset_dimmers:
            print("presetting DIMMERS")
            self.player.sign.set_dimmers(ALL_HIGH, force_update=True)
        if preset_relays:
            print("presetting RELAYS")
            self.player.sign.set_lights(ALL_ON)

    def mode_index(self, current: int, delta: int) -> int:
        """Return a new mode index, wrapping index in both directions."""
        lower, upper = 1, len(self.player.modes) - 1
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

    @abstractmethod
    def button_action(self, button: Button):
        """Respond to the button press."""

    @abstractmethod
    def execute(self):
        """Play the mode."""
 
class SelectMode(Mode):
    """Supports the select mode."""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        #
        previous_mode: int,
    ):
        """"""
        super().__init__(player, name, preset_dimmers=True)
        self.desired_mode = previous_mode
        self.previous_desired_mode = -1

    def button_action(self, button: Button):
        """Respond to the button press."""
        assert self.desired_mode is not None
        match button.name:
            case 'body_back' | 'remote_a' | 'remote_d':
                self.desired_mode = self.mode_index(self.desired_mode, +1)
            case 'remote_b':
                self.desired_mode = self.mode_index(self.desired_mode, -1)
            case 'remote_c':
                # self.desired_mode = 2  # ALL_OFF
                return 222  # Quick change to mode ALL_OFF
            case _:
                raise Exception
        return None

    def execute(self):
        """User presses the button to select 
           the next mode to execute."""
        super().execute()
        new_mode = None
        if self.desired_mode != self.previous_desired_mode:
            # Not last pass.
            # Show user what desired mode number is currently selected.
            self.player.sign.set_lights(ALL_OFF)
            time.sleep(0.5)
            self.player.play_sequence(
                seq_rotate_build_flip(count=self.desired_mode),
                pace=0.20, post_delay=4.0,
            )
            self.previous_desired_mode = self.desired_mode
        else:
            # Last pass.
            # Time elapsed without a button being pressed.
            # Play the selected mode.
            new_mode = self.desired_mode
        return new_mode

class PlayMode(Mode):
    """Base for custom modes."""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        """"""
        super().__init__(player, name, preset_dimmers, preset_relays)
        self.direction = +1

    def button_action(self, button: Button):
        """Respond to the button press."""
        new_mode = None
        match button.name:
            case 'remote_a' | 'body_back':
                new_mode = 0
            case 'remote_c':
                self.player.sign.click()
                self.direction *= -1
            case 'remote_b':
                self.player.sign.click()
                new_mode = self.mode_index(self.player.current_mode, -1)
            case 'remote_d':
                self.player.sign.click()
                new_mode = self.mode_index(self.player.current_mode, +1)
                print("Button Action: ", new_mode)
            case _:
                raise Exception
        return new_mode

class PlaySequenceMode(PlayMode):
    """Supports all sequence-based modes."""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        #
        sequence: Callable,
        pace: tuple[float, ...] | float | None = None,
        stop: int | None = None,
        special: SpecialParams | None = None,
        **kwargs,
    ):
        """"""
        self.sequence = sequence
        self.pace = pace
        self.stop = stop
        self.special = special
        self.kwargs = kwargs
        if isinstance(special, DimmerParams):
            default_trans = (
                pace if isinstance(pace, float) else
                TRANSITION_DEFAULT
            )
            if special.transition_off is None:
                special.transition_off = default_trans
            if special.transition_on is None:
                special.transition_on = default_trans
        super().__init__(
            player, 
            name, 
            preset_dimmers=(special is None),
            preset_relays=(special is not None),
        )

    def play_sequence_once(self):
        """Play established sequence once."""
        self.player.replace_kwarg_values(self.kwargs)
        self.player.play_sequence(
            sequence=self.sequence(**self.kwargs),
            pace=self.pace,
            stop=self.stop,
            special=self.special,
        )

    def execute(self):
        """Play the mode."""
        super().execute()
        while True:
            self.play_sequence_once()

class Sequence(Element):
    """"""
    def __init__(
        self,
        sequence: Callable,
        special: SpecialParams | None = None,
        **kwargs,
    ):
        super().__init__()
        self.sequence = sequence
        self.special = special
        self.kwargs = kwargs
        self.iter = itertools.cycle(sequence(**kwargs))

class NoteSequence(Sequence):
    """"""
    def __init__(
        self,
        step_duration: float, 
        count: int,
        sequence: Callable,
        special: SpecialParams | None = None,
        **kwargs,
    ):
        super().__init__(sequence, special, **kwargs)
        self.step_duration = step_duration
        self.count = count

class PlayMusicMode(PlayMode):
    """4 beats per measure by default.
       Every quarter note gets a beat."""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
    ):
        super().__init__(player, name, preset_dimmers=True)
        #self.bells = self.player.sign.bell_set
        #self.drums = self.player.sign.drum_set
        self.notation = interpret_notation
        self.tempo = 60  # Default

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
        """Return callable to effect dimmer pattern."""
        return lambda: self.player.sign.set_dimmers(pattern)

    def light(
        self, 
        pattern: Any,
        special: SpecialParams | None = None,
    ) -> Callable:
        """Return callable to effect light pattern."""
        print(f"light: {pattern}")
        if isinstance(special, ActionParams):
            result = lambda: special.action(pattern)
        else:
            result = lambda: self.player.sign.set_lights(
                light_pattern=pattern,
                special=special,
            )
        return result

    def relay(self, *indices):
        """Flip ???????????????????"""
        return lambda: self.player.sign.flip_extra_relays(*indices)
    
    def rest(self, symbols: str) -> Rest:
        """Validate symbols and return Rest."""
        duration, pitch, accent, rest = interpret_symbols(symbols)
        if pitch or accent:
            raise ValueError("Rest cannot have pitch or accent.")
        return Rest(duration)

    def act(self, symbols: str, *actions: Callable) -> ActionNote | Rest:
        """Validate symbols and return ActionNote or Rest."""
        duration, pitch, accent, rest = interpret_symbols(symbols)
        if rest:
            return self.rest(symbols)
        #if pitch or accent:
        #    raise ValueError("Action note cannot have pitch or accent.")
        return ActionNote(duration, actions)

    def seq_part(
            self, 
            create_note: Callable[[str], ActionNote | Rest], 
            notation: str, 
            beats=4
    ) -> Part:
        """Produce sequence part from notation."""
        return self.part(
            *interpret_notation(create_note, notation, beats)
        )

    def bell(self, symbols: str) -> BellNote | Rest:
        """Validate symbols and return BellNote or Rest."""
        duration, pitch, accent, rest = interpret_symbols(symbols)
        if rest:
            return self.rest(symbols)
        if accent:
            raise ValueError("Bell note cannot have accent.")
        return BellNote(duration, pitch)

    def bell_part(self, notation: str, beats=4) -> Part:
        """Produce bell part from notation."""
        return self.part(
            *interpret_notation(self.bell, notation, beats)
        )

    def drum(self, symbols: str) -> DrumNote | Rest:
        """Validate symbols and return DrumNote or Rest."""
        duration, pitch, accent, rest = interpret_symbols(symbols)
        if rest:
            return self.rest(symbols)
        if pitch:
            raise ValueError("Drum note cannot have pitch.")
        return rest or DrumNote(duration, accent)

    def drum_part(self, notation: str, beats=4) -> "Part":
        """Produce drum part from notation."""
        return self.part(
            *interpret_notation(self.drum, notation, beats)
        )

    def part(self, *measures: Measure) -> Part:
        """Produce Part."""
        return Part(measures)

    def measure(self, *elements: Element, beats: int = 4) -> Measure:
        """Produce Measure."""
        return Measure(elements, beats=beats)

    def seq(
        self,
        sequence: Callable,
        special: SpecialParams | None = None,
        **kwargs,
    ) -> Callable[[str], ActionNote | Rest]:
        """Return callable to effect each step in sequence."""
        seq = Sequence(
            sequence, special, **kwargs,
        )
        def func(s: str):
            return self.act(s, self.light(next(seq.iter), special))
        return func
    
    def sequence(
        self,
        symbols: str,
        count: int,
        sequence: Callable,
        special: SpecialParams | None = None,
        **kwargs,
    ) -> "NoteSequence":
        """Produce a NoteSequence."""
        step_duration, _, _, _ = interpret_symbols(symbols)
        return NoteSequence(
            step_duration, count, sequence, special, **kwargs,
        )

    def expand_sequences(self, measures: tuple[Measure, ...]):
        """Convert NoteSequence into multiple ActionNotes."""
        for measure in measures:
            if not measure.elements:
                continue
            if not isinstance(measure.elements[0], NoteSequence):
                continue
            assert len(measure.elements) == 1, \
                "NoteSequence must be the only element in the measure."
            seq = measure.elements[0]
            assert isinstance(seq, "NoteSequence")
            actions = itertools.cycle(seq.sequence(**seq.kwargs))
            measure.elements = tuple(
                ActionNote(
                    duration=seq.step_duration,
                    actions=(
                        self.light(
                            pattern=next(actions),
                            special=seq.special,
                        ),
                    )
                )
                for c in range(seq.count)
            )

    def prepare_for_playing(self, measures):
        """All manipulation required before playing measures."""
        self.expand_sequences(measures)

    def play_measures(self, *measures: Measure):
        """Play sequential measures."""
        for measure in measures:
            print("PLAYING MEASURE")
            beat = 0
            self.prepare_for_playing(measures)
            assert all(
                isinstance(e, BaseNote)
                for e in measure.elements
            )
            for element in measure.elements:
                start = time.time()
                assert isinstance(element, BaseNote)
                if isinstance(element, DrumNote):
                    self.player.sign.drum_set.play(element.accent)
                else:
                    element.execute()
                wait = (element.duration) * self.pace
                self.player.wait(wait, elapsed = time.time() - start)
                beat += element.duration
            wait = max(0, measure.beats - beat) * self.pace
            self.player.wait(wait)

    def play_parts(self, *parts: Part):
        """Merge parts into new sequence of measures, and then play."""
        assert parts
        measure_count = [len(p.measures) for p in parts]
        assert all(c == measure_count[0] for c in measure_count)
        for part in parts:
            self.prepare_for_playing(part.measures)
        concurrent_measures = zip(*(p.measures for p in parts))
        new_measures = [
            merge_concurrent_measures(measure_set)
            for measure_set in concurrent_measures
        ]
        self.play_measures(*new_measures)
