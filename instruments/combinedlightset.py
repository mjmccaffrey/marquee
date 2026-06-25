"""Marquee Lighted Sign Project - combinedlightset"""

from collections.abc import Sequence
from dataclasses import dataclass
import logging
from typing import cast

from devices.lightcontroller import ChannelUpdate
from .lightset import LightSet
from .lightsetinterface import SavedState

log = logging.getLogger('marquee.' + __name__)


@dataclass
class CombinedLightSet:
    """"""
    ls1: LightSet
    ls2: LightSet

    def __post_init__(self):
        """"""
        self.channels = (
            list(self.ls1.channels) + list(self.ls2.channels)
        )
        self.count = self.ls1.count + self.ls2.count
        self.gamut = self.ls1.gamut
        self.speed_factor = self.ls1.speed_factor

    def set_channels(self, *args, **kwargs) -> None:
        """"""
        assert self.ls2 is not None
        indices = kwargs.get('indices')
        print(f"**{indices=}")
        if indices is None:
            self.ls1.set_channels(*args, **kwargs)
            self.ls2.set_channels(*args, **kwargs)
        else:
            ls1_indices = {
                i 
                for i in indices
                if i < self.ls1.count
            }
            ls2_indices = {
                i - self.ls1.count
                for i in indices
                if i >= self.ls1.count
            }
            print(f'{ls1_indices=} {ls2_indices=})')
            if ls1_indices:
                kwargs['indices'] = ls1_indices
                self.ls1.set_channels(*args, **kwargs)
            if ls2_indices:
                kwargs['indices'] = ls2_indices
                self.ls2.set_channels(*args, **kwargs)

    def set_relays(self, *args, **kwargs) -> None:
        """"""
        raise NotImplementedError

    def update_channels(self, updates: Sequence['ChannelUpdate']):
        """"""
        self.ls1.update_channels(updates[:self.ls1.count])
        self.ls2.update_channels(updates[self.ls1.count:])

    def brightnesses(self) -> list[int]:
        """"""
        return self.ls1.brightnesses() + self.ls2.brightnesses()

    def current_state(self) -> 'SavedState':
        """"""
        states = zip(
            self.ls1.current_state(), self.ls2.current_state()
        )
        return cast(SavedState, tuple(p + s for p, s in states))

    def restore_state(self, state: 'SavedState', transition: float) -> None:
        """"""
        ls1_state = tuple(tuple(t[:self.ls1.count]) for t in state)
        ls2_state = tuple(tuple(t[self.ls1.count:]) for t in state)
        self.ls1.restore_state(cast(SavedState, ls1_state), transition)
        self.ls2.restore_state(cast(SavedState, ls2_state), transition)

    @property
    def brightness_factor(self) -> float:
        """"""
        return self._brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None:
        """"""
        self._brightness_factor = value
        self.ls1.brightness_factor = value
        self.ls2.brightness_factor = value

    def calibrate(self) -> None:
        """"""
        raise NotImplementedError
    
