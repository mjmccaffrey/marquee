"""Marquee Lighted Sign Project - dynamicmode"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .performancemode import PerformanceMode
from specialparams import ChannelParams

@dataclass(kw_only=True)
class DynamicMode(PerformanceMode, ABC):
    """"""
    sequence_mode_name: str

    # def __post_init__(self) -> None:
    #     """Initialize."""
    #     super().__post_init__()

    def execute(self):
        """Execute sequence_mode_name as child, with new 
           ChannelParams generated when requested by LightSet."""
        index = self.lookup_mode_index(self.sequence_mode_name)
        self.mode = self.player.modes[index]
        kwargs = (
            self.player.replace_kwarg_values(self.mode.kwargs) |
            {'special': ChannelParams(generate=self.generate_special)}
        )
        mode_instance = self.mode.cls(
            player=self.player,
            index=self.mode.index,
            name=self.mode.name, 
            parent=self,
            **kwargs,
        )
        mode_instance.execute()

    @abstractmethod
    def generate_special(self) -> ChannelParams:
        """Return new set of ChannelParams."""

