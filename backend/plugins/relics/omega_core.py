from dataclasses import dataclass
from dataclasses import field

from plugins.relics._base import RelicBase


@dataclass
class OmegaCore(RelicBase):
    """Massive stat boost for 10 turns, then escalating HP drain."""

    id: str = "omega_core"
    name: str = "Omega Core"
    stars: int = 5
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 5.0, "defense": 5.0})
