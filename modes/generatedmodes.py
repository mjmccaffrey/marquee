"""Marquee Lighted Sign Project - generatedmodes"""

from dataclasses import dataclass
from typing_extensions import override

from . import RandomFade, ModeDefinition
from .abstract.mode import BaseMode


@dataclass(kw_only=True)
class GeneratedModes(RandomFade):
    """"""
    light_index: int | None = None  # None => parent

    @override
    def close(self) -> None:
        """Delete all tasks by all created instances."""
        assert self.light_index is None
        for instance in self.instances:
            self.tasks.delete_owned_by(instance)
        super().close()

    @override
    def execute(self) -> None:
        """"""
        if self.light_index is None:
            self.instances = [
                self.generate_mode(i)
                for i in range(self.lights.count)
            ]
        else:
            print(f"GM: {self.light_index}")
            self.update_light_schedule_next(self.light_index)

    def generate_mode(self, light_index: int) -> BaseMode:
        """"""
        mode = self.create_mode_instance(
            mode_definition=ModeDefinition(
                name=f'generated_mode_{light_index:02}',
                cls=GeneratedModes,
            ),
            kwargs=dict(
                background=True,
                transition=self.transition,
                duration=self.duration,
                color_set_name=self.color_set_name,
                light_index=light_index,
            ),
            parent=self,
        )
        self.schedule(mode.execute, light_index * 2)
        return mode

    @override
    def update_light_schedule_next(self, index: int) -> None:
        """"""
        print(f"{self.light_index=} {index=}")
        super().update_light_schedule_next(index)
