from dataclasses import dataclass
from dataclasses import field

from plugins.relics._base import RelicBase


@dataclass
class RustyBuckle(RelicBase):
    """Bleeds lowest-HP ally and triggers Aftertaste as HP drops."""

    id: str = "rusty_buckle"
    name: str = "Rusty Buckle"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {})
