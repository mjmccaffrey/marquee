"""Marquee Lighted Sign Project - setup_devices"""

from dataclasses import dataclass, field

def default_adjustments() -> dict[str, int]:
    """Return default brightness adjustments."""
    return {
        '0': 0, '1': 10, '2': 20, '3': 30, '4': 40,
        '5': 50, '6': 60, '7': 70, '8':80, '9': 90,
        'A': 100, 'F': 25,
    }

@dataclass
class Bulb:
    """ABC for any light bulb."""
    wattage_actual: float
    wattage_reference: float
    adjustments: dict[str, int] = field(default_factory=default_adjustments)

@dataclass
class DimBulb(Bulb):
    """Base for incandescents, basic dimmable LED bulbs, etc."""

@dataclass
class SmartBulb(Bulb):
    """Base for Hue bulbs, etc."""

Halco_S14_Transparent_Colored = DimBulb(
    wattage_actual=11,
    wattage_reference=11,
)

Hue_BR30_Enhanced_Color = SmartBulb(
    wattage_actual=12.5,
    wattage_reference=85,
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
