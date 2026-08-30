"""Marquee Lighted Sign Project - music_concrete"""

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, replace
import logging
from typing_extensions import override

from devices.device_schemas import DeviceName
from instruments import BellSet, Buzzer, DrumSet, Ringer
from .music_abstract import (
    Element, Note, Accented, Pitched,
    PlayableNote, ReleasableNote, PlayableReleasableNote,
    DinNote, PlayableDinNote, LightNote, PlayableLightNote,
)
log = logging.getLogger('marquee.' + __name__)


@dataclass(frozen=True, kw_only=True)
class Rest(Note):
    """Musical rest."""
    device: None = None


@dataclass(frozen=True, kw_only=True)
class PlayableRest(Rest, PlayableNote):
    """Musical rest."""
    instrument: None = None

    @override
    def play(self, bps: float) -> None:
        """Play single rest (do nothing)."""
        raise RuntimeError("PLAYING REST")


@dataclass(frozen=True, kw_only=True)
class ActionNote(Note):
    """Note to execute arbitrary actions."""
    device: None = None
    action: Callable[[], None]


@dataclass(frozen=True, kw_only=True)
class PlayableActionNote(ActionNote, PlayableNote):
    """Playable note to execute arbitrary actions."""
    instrument: None = None

    @override
    def play(self, bps: float) -> None:
        """Play single ActionNote."""
        self.action()


@dataclass(frozen=True, kw_only=True)
class BellNote(ReleasableNote, Pitched):
    """Note to strike and release 1 or more bells."""
    device: DeviceName = DeviceName.BELLS


@dataclass(frozen=True, kw_only=True)
class PlayableBellNote(BellNote, PlayableReleasableNote):
    """Note to strike and release 1 or more bells."""
    instrument: BellSet

    @override
    def play(self, bps: float) -> None:
        """Play BellNote."""
        self.instrument.play(self.pitches)
        self.schedule_release(self.instrument.release_time)

    @override
    def release(self) -> None:
        """Release BellNote."""
        self.instrument.release(self.pitches)


@dataclass(frozen=True, kw_only=True)
class DrumNote(Note, Accented, Pitched):
    """Note to sound relays."""
    device: DeviceName = DeviceName.DRUMS


@dataclass(frozen=True, kw_only=True)
class PlayableDrumNote(DrumNote, PlayableNote):
    """Note to sound relays."""
    instrument: DrumSet

    @override
    def play(self, bps: float) -> None:
        """Play DrumNote."""
        self.instrument.play(self.accent, self.pitches)


@dataclass(frozen=True, kw_only=True)
class LightChannelNote(LightNote):
    """Note to execute light channel actions."""


@dataclass(frozen=True, kw_only=True)
class PlayableLightChannelNote(PlayableLightNote):
    """Note to execute light channel actions."""

    @override
    def play(self, bps: float) -> None:
        """Play single LightChannelNote."""
        if self.kwargs:
            self.instrument.set_channels(**self.kwargs)


@dataclass(frozen=True, kw_only=True)
class LightRelayNote(LightNote):
    """Note to execute light relay actions."""


@dataclass(frozen=True, kw_only=True)
class PlayableLightRelayNote(PlayableLightNote):
    """Note to execute light relay actions."""

    @override
    def play(self, bps: float) -> None:
        """Play single LightRelayNote."""
        if self.kwargs:
            self.instrument.set_relays(**self.kwargs)


@dataclass(frozen=True, kw_only=True)
class BuzzerNote(DinNote):
    """"""
    device: DeviceName = DeviceName.BUZZER


@dataclass(frozen=True, kw_only=True)
class PlayableBuzzerNote(BuzzerNote, PlayableDinNote):
    """"""
    instrument: Buzzer


@dataclass(frozen=True, kw_only=True)
class RingerNote(DinNote):
    """"""
    device: DeviceName = DeviceName.RINGER


@dataclass(frozen=True, kw_only=True)
class PlayableRingerNote(RingerNote, PlayableDinNote):
    """"""
    instrument: Ringer


@dataclass(frozen=True, kw_only=True)
class NoteGroup(Note):
    """Contains notes to play concurrently."""
    device: None = None
    instrument: None = None
    notes: tuple[Note, ...]


@dataclass(frozen=True, kw_only=True)
class PlayableNoteGroup(PlayableNote):
    """Contains notes to play concurrently."""
    notes: tuple[PlayableNote, ...]

    @override
    def play(self, bps: float) -> None:
        """Play all notes in group, not quite concurrently."""
        for note in self.notes:
            note.play(bps)


NOTE_CONVERSIONS: dict[type[Element], type[PlayableNote]] = {
    Rest: PlayableRest,
    ActionNote: PlayableActionNote,
    BellNote: PlayableBellNote,
    DrumNote: PlayableDrumNote,
    LightChannelNote: PlayableLightChannelNote,
    LightRelayNote: PlayableLightRelayNote,
    BuzzerNote: PlayableBuzzerNote,
    RingerNote: PlayableRingerNote,
}


@dataclass(frozen=True)
class Measure(Element):
    """Musical measure containing notes and / or implicit rests."""
    elements: tuple[Element, ...]
    beats: int


@dataclass(frozen=True)
class PlayableMeasure(Element):
    """Musical measure containing playable notes and / or implicit rests."""
    notes: tuple[PlayableNote, ...]
    beats: int


@dataclass(frozen=True)
class Part(Element):
    """Musical part containing measures.
       All measures have the same number of beats."""
    measures: tuple[Measure, ...]
    default_accent: int = 0

    def __post_init__(self) -> None:
        """Apply default accent."""
        if self.default_accent:
            self._apply_accent()

    def _apply_accent(self) -> None:
        """Apply default accent."""
        for measure in self.measures:
            assert isinstance(measure, Measure)
            elements = tuple(
                replace(e, accent=self.default_accent)
                if isinstance(e, Accented) and not e.accent else
                e
                for e in measure.elements
            )
            object.__setattr__(measure, 'elements', elements)



@dataclass(frozen=True)
class Section(Element):
    """Musical section containing parts and meta info.
       All measures have the same number of beats."""
    parts: tuple[Part, ...]
    beats: int
    tempo: int = 0
    measures: tuple[Measure, ...] = field(init=False)

    def __post_init__(self) -> None:
        """"""
        if self.beats is not None:
            self._apply_beats()
        self._convert_parts_to_measures()

    def _apply_beats(self) -> None:
        """Apply default # of beats to all Measures
           in all Parts in the Section."""
        for part in self.parts:
            measures = tuple(
                replace(measure, beats=self.beats)
                for measure in part.measures
            )
            object.__setattr__(part, 'measures', measures)

    def _convert_parts_to_measures(self) -> tuple[Measure, ...]:
        """Merge parts into single sequence of measures."""
        self._equalize_part_lengths()
        concurrent_measures = zip(*(part.measures for part in self.parts))
        return tuple(
            self._merge_measures(measure_set)
            for measure_set in concurrent_measures
        )

    def _equalize_part_lengths(self) -> None:
        """Make all parts have the same # of measures."""
        longest = max(len(part.measures) for part in self.parts)
        for part in self.parts:
            if len(part.measures) < longest:
                pad = Measure(
                    elements=(Rest(duration=0.0),), 
                    beats=part.measures[-1].beats,
                )
                short = longest - len(part.measures)
                measures = part.measures + (pad,) * short
                object.__setattr__(part, 'measures', measures)

    @staticmethod
    def _get_concurrent_notes(
        elements_in: list[Iterator],
        beat_next: list[float | None],
        beat: float,
    ) -> Note | None:
        """Return all notes occuring on beat; 
        multiple notes as NoteGroup,
        a single note, or None."""
        concurrent = []
        for i in range(len(elements_in)):
            if beat_next[i] == beat:
                element = next(elements_in[i], None)
                if element is None:
                    beat_next[i] = None
                else:
                    assert isinstance(element, Note)
                    beat_next[i] = beat + element.duration
                    if not isinstance(element, Rest):
                        concurrent.append(replace(element, duration=0))
        if len(concurrent) > 1:
            return NoteGroup(notes=tuple(concurrent))
        elif len(concurrent) == 1:
            return concurrent[0]
        else:
            return None

    @staticmethod
    def _merge_measures(measures: tuple[Measure, ...]) -> Measure:
        """Convert aligned measure from each Part into single measure
        of (non-rest) notes with 0 duration, padded with rests."""

        beats = measures[0].beats
        assert all(m.beats == beats for m in measures)
        elements_in: list[Iterator] = [iter(m.elements) for m in measures]
        elements_out: list[Element] = []
        beat_next: list[float | None] = [0.0] * len(measures)
        beat, rest_accumulated = 0.0, 0.0
        while any(bn is not None for bn in beat_next):
            concurrent = Section._get_concurrent_notes(
                elements_in, beat_next, beat,
            )
            if concurrent is not None:
                if rest_accumulated:
                    elements_out.append(Rest(duration=rest_accumulated))
                    rest_accumulated = 0.0
                elements_out.append(concurrent)
            next_beat = min(
                (bn for bn in beat_next if bn is not None), default=beats,
            )
            rest_accumulated += next_beat - beat
            beat = next_beat
        if rest_accumulated:
            elements_out.append(Rest(duration=rest_accumulated))
        return Measure(tuple(elements_out), beats=beats)


@dataclass(frozen=True)
class Piece(Element):
    """Series of Sections and Parts. 
       Number of beats across sections and parts may vary."""
    groups: tuple[Section | Part, ...]
    tempo: int = 0


