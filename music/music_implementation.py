"""Marquee Lighted Sign Project - music_implementation"""

from dataclasses import replace
from itertools import chain
from functools import partial
import time
from typing import Any, Callable, Iterator

from event import Event
from .music_elements import (
    ActionNote, BaseNote, DrumNote, Element, Measure, NoteGroup,
    Part, Rest, SequenceMeasure,
)
from playerinterface import PlayerInterface
from specialparams import (
    ActionParams, ChannelParams, SpecialParams,
)


def _set_player(the_player: PlayerInterface) -> None:
    """Set the Player object used throughout this module."""
    global player
    player = the_player


def prepare_parts(parts: tuple[Part, ...]) -> tuple[Measure, ...]:
    """Expand SequenceMeasures.
       Make all parts the same length.
       Merge parts into single sequence of Measures."""
    for part in parts:
        expand_sequence_measures(part.measures)
        validate_measures(part.measures)
    equalize_part_lengths(parts)
    concurrent_measures = zip(*(part.measures for part in parts))
    return tuple(
        merge_concurrent_measures(measure_set)
        for measure_set in concurrent_measures
    )


def merge_concurrent_measures(measures: tuple[Measure, ...]) -> Measure:
    """Convert measure from each part into single measure
    of (non-rest) notes with 0 duration, padded with rests."""

    def get_concurrent_notes(beat: float) -> list[BaseNote]:
        """Return all notes occuring on beat."""
        result = []
        for i, _ in enumerate(measures):
            if beat_next[i] == beat:
                element = next(elements_in[i], None)
                if element is None:
                    beat_next[i] = None
                else:
                    assert isinstance(element, BaseNote)
                    beat_next[i] = beat + element.duration
                    if not isinstance(element, Rest):
                        result.append(replace(element, duration=0))
        return result

    def convert_concurrent_notes(concurrent: list[BaseNote]) -> Element | None:
        """Return > 1 notes as NoteGroup, 
            1 note as itself, and 0 notes as None."""
        if len(concurrent) > 1:
            result = NoteGroup(tuple(concurrent))
        elif len(concurrent) == 1:
            result = concurrent[0]
        else:
            result = None
        return result

    beats = measures[0].beats
    assert all(m.beats == beats for m in measures)
    elements_in: list[Iterator] = [iter(m.elements) for m in measures]
    elements_out: list[Element] = []
    beat_next: list[float | None] = [0.0 for _ in measures]
    beat, rest_accumulated = 0.0, 0.0
    while any(bn is not None for bn in beat_next):
        concurrent = get_concurrent_notes(beat)
        out = convert_concurrent_notes(concurrent)
        if out is not None:
            if rest_accumulated:
                elements_out.append(Rest(rest_accumulated))
                rest_accumulated = 0.0
            elements_out.append(out)
        next_beat = min(
            (bn for bn in beat_next if bn is not None),
            default=beats
        )
        rest_accumulated += next_beat - beat
        beat = next_beat
    if rest_accumulated:
        elements_out.append(Rest(rest_accumulated))
    return Measure(tuple(elements_out), beats=beats)


def expand_sequence_measures(measures: tuple[Measure, ...]) -> None:
    """Populate SequenceMeasures with ActionNotes."""
    for measure in measures:
        if not isinstance(measure, SequenceMeasure):
            continue
        assert isinstance(measure, SequenceMeasure)
        elements = tuple(
            ActionNote(
                duration=measure.step_duration,
                actions=(
                    _light(
                        next(measure.patterns),
                        measure.special,
                    ),
                )
            )
            for _ in range(measure.count)
        )
        object.__setattr__(measure, 'elements', elements)


def validate_measures(measures: tuple[Measure, ...]) -> None:
    """Confirm that measures are ready to play."""
    assert all(
        isinstance(element, BaseNote)
        for measure in measures
        for element in measure.elements
    )
    assert all(
        sum(note.duration) <= measure.beats  # type: ignore
        for measure in measures
        for note in measure.elements
    )


def equalize_part_lengths(parts: tuple[Part, ...]) -> None:
    """Make all parts have the same # of measures."""
    longest = max(len(part.measures) for part in parts)
    for part in parts:
        if len(part.measures) < longest:
            pad = Measure(elements=(), beats=part.measures[-1].beats)
            measures = tuple(
                part.measures[i] if i < len(part.measures) else pad
                for i in range(longest)
            )
            object.__setattr__(part, 'measures', measures)


def events_in_measure(measure: Measure, start: float) -> list[Event]:
    """Return events for all notes in measure."""
    beat = 0.0 
    result = []
    for element in measure.elements:
        assert isinstance(element, (BaseNote, NoteGroup))
        result.append(
            Event(
                action = partial(element.play, player),
                owner = player,
                due = start + beat
            )
        )
        # if element.duration:
        #     player.wait(element.duration, time.time() - start)
        #     start = time.time()
        beat += element.duration
        if beat > measure.beats:
            raise ValueError("Too many actual beats in measure.")
    # # Play implied rests at end of measure
    # player.wait(measure.beats - beat, time.time() - start)
    return result

def events_in_measures(measures: tuple[Measure, ...], tempo: int) -> list[Event]:
    """Return events for all notes in all measures."""
    start = time.time()
    pace = 60 / tempo
    duration = pace * measures[0].beats
    events_by_measure = chain(
        events_in_measure(measure, start + index * duration)
        for index, measure in enumerate(measures)
    )
    events_combined = [
        event
        for measure in events_by_measure
        for event in measure
    ]
    return events_combined


def play_measures(measures: tuple[Measure, ...], tempo: int):
    """Convert measures to events, add to event queue."""
    events = events_in_measures(measures, tempo)
    player.event_queue.bulk_add(events)


def _channel(pattern: str) -> Callable:
    """Return callable to effect dimmer pattern."""
    return lambda: player.lights.set_channels(pattern)


def _channel_sequence(brightness: int, transition: float) -> Callable:
    """Return callable to effect state of specified channels."""
    def func(lights: list[int]):
        player.lights.set_channel_subset(lights, brightness, transition)
    return func


def _channel_sequence_flip(transition: float) -> Callable:
    """Return callable to flip state of specified channels."""
    def func(lights: list[int]):
        brightness = 0 if player.lights.controller.brightnesses()[lights[0]] else 100
        player.lights.set_channel_subset(lights, brightness, transition)
    return func


def _light(
    pattern: Any,
    special: SpecialParams | None = None,
) -> Callable:
    """Return callable to effect light pattern."""
    if isinstance(special, ChannelParams):
        if special.transition_off is None:
            special.transition_off = TRANSITION_DEFAULT
        if special.transition_on is None:
            special.transition_on = TRANSITION_DEFAULT
    if isinstance(special, ActionParams):
        result = lambda: special.action(pattern)
    else:
        result = lambda: player.lights.set_relays(
            light_pattern=pattern,
            special=special,
        )
    return result

