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
    ls0: LightSet
    ls1: LightSet

    def __post_init__(self):
        """"""
        self.channels = (
            list(self.ls0.channels) + list(self.ls1.channels)
        )
        self.colors = self.ls0.colors
        self.count = self.ls0.count + self.ls1.count
        self.gamut = self.ls0.gamut
        self.speed_factor = self.ls0.speed_factor

    def _convert_index(
        self,
        index: Sequence[int] | int | None,
    ) -> list[int] | None:
        """Return normalized index list.  If index is None, 
           return complete index list in scattered order."""
        match index:
            case Sequence():
                result = list(index)
            case None:
                result = None
            case int():
                result = [index]
        return result

    def set_channels(self, *args, **kwargs) -> None:
        """"""
        if kwargs.get('group') is not None:  # Kludge.
            self.ls0.set_channels(*args, **kwargs)
            self.ls1.set_channels(*args, **(kwargs | dict(state_only=True)))
            return
        assert self.ls1 is not None
        index = self._convert_index(kwargs.get('index'))
        if index is None:
            self.ls0.set_channels(*args, **kwargs)
            self.ls1.set_channels(*args, **kwargs)
        else:
            ls0_index = [
                i 
                for i in index
                if i < self.ls0.count
            ]
            ls1_index = [
                i - self.ls0.count
                for i in index
                if i >= self.ls0.count
            ]
            if ls0_index:
                kwargs['index'] = ls0_index
                self.ls0.set_channels(*args, **kwargs)
            if ls1_index:
                kwargs['index'] = ls1_index
                self.ls1.set_channels(*args, **kwargs)

    def set_relays(self, *args, **kwargs) -> None:
        """"""
        raise NotImplementedError

    def update_channels(self, updates: Sequence['ChannelUpdate']):
        """"""
        self.ls0.update_channels(updates[:self.ls0.count])
        self.ls1.update_channels(updates[self.ls0.count:])

    def brightnesses(self) -> list[int]:
        """"""
        return self.ls0.brightnesses() + self.ls1.brightnesses()

    def current_state(self) -> 'SavedState':
        """"""
        states = zip(
            self.ls0.current_state(), self.ls1.current_state()
        )
        return cast(SavedState, tuple(p + s for p, s in states))

    def restore_state(self, state: 'SavedState', transition: float) -> None:
        """"""
        ls0_state = tuple(tuple(t[:self.ls0.count]) for t in state)
        ls1_state = tuple(tuple(t[self.ls0.count:]) for t in state)
        self.ls0.restore_state(cast(SavedState, ls0_state), transition)
        self.ls1.restore_state(cast(SavedState, ls1_state), transition)

    @property
    def brightness_factor(self) -> float:
        """"""
        return self._brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None:
        """"""
        self._brightness_factor = value
        self.ls0.brightness_factor = value
        self.ls1.brightness_factor = value

    def calibrate(self) -> None:
        """"""
        raise NotImplementedError
    
