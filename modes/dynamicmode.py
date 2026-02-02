"""Marquee Lighted Sign Project - dynamicmode"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .performancemode import PerformanceMode
from specialparams import ChannelParams

@dataclass(kw_only=True)
class DynamicMode(PerformanceMode, ABC):
    """Utilizes ChannelParams.generate to insert
       dynamic channel parameters. Of limited use."""
    sequence_mode_name: str

    @abstractmethod
    def generate(self, special: ChannelParams) -> ChannelParams:
        """Return new set of ChannelParams."""

    def execute(self):
        """Execute sequence_mode_name as child, with new 
           ChannelParams generated when requested by LightSet."""
        index = self.lookup_mode_index(self.sequence_mode_name)
        kwargs = dict(
            special=ChannelParams(generate=self.generate)
        )
        mode_instance = self.create_mode_instance(
            mode_index=index,
            kwargs=kwargs,
            parent=self,
        )
        mode_instance.execute()

