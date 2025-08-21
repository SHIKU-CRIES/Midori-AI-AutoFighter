from dataclasses import dataclass
from dataclasses import field

from plugins.relics._base import RelicBase


@dataclass
class ParadoxHourglass(RelicBase):
    """May kill a random ally then greatly boost survivors and weaken foes."""

    id: str = "paradox_hourglass"
    name: str = "Paradox Hourglass"
    stars: int = 5
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 2.0, "defense": 2.0})
