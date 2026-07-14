"""Marquee Lighted Sign Project - generatedmodes"""

from dataclasses import dataclass
from typing_extensions import override

from . import RandomFade, ModeDefinition


@dataclass(kw_only=True)
class GeneratedModes(RandomFade):
    """"""
    light_index: int | None = None  # None => parent

    @override
    def execute(self) -> None:
        """"""
        if self.light_index is None:
            for light_index in range(self.lights.count):
                self.generate_mode(light_index)
            self.schedule(self.exit, 120)
        else:
            self.update_light_schedule_next(self.light_index)

    def exit(self) -> None:
        """"""
        self.delete_mode_instance(self.index)

    def generate_mode(self, light_index: int):
        """"""
        mode = self.create_mode_instance(
            mode_definition=ModeDefinition(
                name='cs_rotate',
                cls=RandomFade,
            ),
            kwargs=dict(
                background=True,
                parent=self,
                transition=self.transition,
                duration=self.duration,
                color_set_name=self.color_set_name,
                light_index=light_index,
            ),
            parent=self,
        )
        self.schedule(mode.execute)

