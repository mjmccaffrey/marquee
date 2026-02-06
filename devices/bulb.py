"""Marquee Lighted Sign Project - setup_devices"""

from dataclasses import dataclass, field

from . import rgbxy

def default_adjustments() -> dict[str, int]:
    """Return default brightness adjustments."""
    return {
        '0': 0, '1': 10, '2': 20, '3': 30, '4': 40,
        '5': 50, '6': 60, '7': 70, '8':80, '9': 90,
        'A': 100, 'F': 25,
    }

@dataclass(kw_only=True)
class Bulb:
    """ABC for any light bulb."""
    gamut: rgbxy.Gamut | None
    wattage_actual: float
    wattage_reference: float
    adjustments: dict[str, int] = field(default_factory=default_adjustments)

@dataclass(kw_only=True)
class DimBulb(Bulb):
    """Base for incandescents, basic dimmable LED bulbs, etc."""
    gamut: None = None

class SmartBulb(Bulb):
    """Base for smart bulbs such as Hue."""

class HueBulb(SmartBulb):
    """Hue bulbs."""
    
Halco_S14_Transparent_Colored = DimBulb(
    wattage_actual=11,
    wattage_reference=11,
)
Hue_BR30_Enhanced_Color = HueBulb(
    wattage_actual=12.5,
    wattage_reference=85,
    gamut = rgbxy.GamutC,
)
Sylvania_G25_Frosted_40 = DimBulb(
    wattage_actual=40,
    wattage_reference=40,
    adjustments={
        '0': 0, '1': 15, '2': 20, '3': 30, '4': 40,
        '5': 50, '6': 60, '7': 70, '8':80, '9': 90,
        'A': 100, 'F': 23,
    }
)
Sylvania_G40_Frosted_100 = DimBulb(
    wattage_actual=100,
    wattage_reference=100,
)

