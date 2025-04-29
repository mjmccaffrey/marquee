from music import *
from definitions import *
from sequence_defs import *
import pytest

# 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀

def test_sequence_part():
    assert sequence_part(
        "  ♩ ♩ ♩ ♩ | ♩  ",
        sequence(all_on, measures=2),
        sequence(all_off),
    ) == Part(
        (
            Measure(
                (
                    ActionNote(
                        1,
                        (
                            
                        )
                    ),
                )
            ),
        )
    )
# def test_merge_1_part_content():
#     measure = Measure(
#         (
#             Rest(0.5),
#             DrumNote(1, ""),
#             Rest(0.5),
#             Rest(1),
#             DrumNote(1, "^"),
#         ),
#         beats=4,
#     ),
#     assert merge_concurrent_measures(measure) == Measure(
#         elements=(
#             Rest(0.5), 
#             DrumNote(0, ""), 
#             Rest(2.5), 
#             DrumNote(0, "^"), 
#             Rest(1.0),
#         ),
#         beats=4,
#     )

# def merged_parts() -> list[Measure]:
#     parts = (
#         Part((
#                 Measure(
#                     (
#                         Rest(1),
#                         BellNote(1 ,"A"),
#                         Rest(1),
#                         BellNote(1, "B"),
#                     ),
#                     beats=4),
#         )),
#         Part((
#                 Measure(
#                     (
#                         Rest(0.5),
#                         DrumNote(1, ""),
#                         Rest(0.5),
#                         Rest(1),
#                         DrumNote(1, "^"),
#                     ),
#                     beats=4),
#         )),
#     )
#     measures = zip(*(p.measures for p in parts))
#     new_measures = [
#         merge_concurrent_measures(measure)
#         for measure in measures
#     ]
#     return new_measures

# def test_merge_2_parts_content():
#     assert merged_parts() == [
#         Measure(
#             elements=(
#                 Rest(0.5), DrumNote(0, ""), Rest(0.5), BellNote(0, "A"), 
#                 Rest(2.0), NoteGroup((BellNote(0, "B"), DrumNote(0, "^"))),
#                 Rest(1.0),
#             ),
#             beats=4,
#         )
#     ]
