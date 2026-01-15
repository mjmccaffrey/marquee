"""Marquee Lighted Sign Project - dynamictest"""

from .performancemode import PerformanceMode
from specialparams import ChannelParams

class DynamicTest(PerformanceMode):
    """"""
    sequence_mode_name: str

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        index = self.lookup_mode_index(self.sequence_mode_name)
        self.mode = self.player.modes[index]
        kwargs = (
            self.player.replace_kwarg_values(self.mode.kwargs) |
            {'parent': self} | 
            {'special': self.generate_special}
        )
        mode_instance = self.mode.cls(
            player=self.player,
            index=self.mode.index,
            name=self.mode.name, 
            **kwargs,
        )
        mode_instance.execute()

    def generate_special(self) -> ChannelParams:
        """"""
        delay = self.mode.kwargs['delay']
        return ChannelParams(
            brightness_on=100,
            brightness_off=100,
            color_on=self.lights.colors.random(),
            color_off=self.lights.colors.random(),
            generate=self.generate_special,
            trans_on=delay,
            trans_off=delay,
        )

        # COULD CLASSIFY THIS AS A BACKGROUND MODE...

        # mode_instance = mode.cls(
        #     player=self,
        #     index=mode.index,
        #     name=mode.name, 
        #     **self.replace_kwarg_values(mode.kwargs),
        # )

        # SequenceMode(
        #     player=self.player,
        #     index=999999,
        #     name="SelectMode sequence player",
        #     sequence=lambda: rotate_build_flip(count=self.desired),
        #     pre_delay = 0.5,
        #     delay=0.20, 
        #     repeat=False,
        #     special=self.special,
        # ).execute()


