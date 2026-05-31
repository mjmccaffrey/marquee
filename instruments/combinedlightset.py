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
    primary: LightSet
    secondary: LightSet

    def __post_init__(self):
        """"""
        self.count = self.primary.count + self.secondary.count
        self.gamut = self.primary.gamut

    def set_channels(self, **kwargs) -> None:
        """"""
        assert self.secondary is not None
        indices = kwargs.get('indices')
        if indices is None:
            self.primary.set_channels(**kwargs)
            self.secondary.set_channels(**kwargs)
        else:
            p_indices = {
                i for i in indices
                if i < self.primary.count
            }
            s_indices = indices - p_indices
            if p_indices:
                kwargs['indices'] = p_indices
                self.primary.set_channels(**kwargs)
            if s_indices:
                kwargs['indices'] = s_indices
                self.secondary.set_channels(**kwargs)

    def set_relays(self, **kwargs) -> None:
        """"""
        raise NotImplementedError

    def update_channels(self, updates: Sequence['ChannelUpdate']):
        """"""
        self.primary.update_channels(updates[:self.primary.count])
        self.secondary.update_channels(updates[self.primary.count:])

    def brightnesses(self) -> list[int]:
        """"""
        return self.primary.brightnesses() + self.secondary.brightnesses()

    def current_state(self) -> 'SavedState':
        """"""
        states = zip(
            self.primary.current_state(), self.secondary.current_state()
        )
        return cast(SavedState, tuple(p + s for p, s in states))

    def restore_state(self, state: 'SavedState', transition: float) -> None:
        """"""
        p_state = tuple(tuple(t[:self.primary.count]) for t in state)
        s_state = tuple(tuple(t[self.primary.count:]) for t in state)
        self.primary.restore_state(cast(SavedState, p_state), transition)
        self.secondary.restore_state(cast(SavedState, s_state), transition)

    @property
    def brightness_factor(self) -> float:
        """"""
        return self._brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None:
        """"""
        self._brightness_factor = value
        self.primary.brightness_factor = value
        self.secondary.brightness_factor = value

