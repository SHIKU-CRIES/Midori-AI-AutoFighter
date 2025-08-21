from dataclasses import dataclass
from dataclasses import field

from plugins.relics._base import RelicBase


@dataclass
class SoulPrism(RelicBase):
    """Revives fallen allies at 1% HP with heavy Max HP penalty and small buffs."""

    id: str = "soul_prism"
    name: str = "Soul Prism"
    stars: int = 5
    effects: dict[str, float] = field(default_factory=lambda: {"defense": 0.05, "mitigation": 0.05})
