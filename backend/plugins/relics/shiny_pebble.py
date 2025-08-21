from dataclasses import dataclass
from dataclasses import field

from plugins.relics._base import RelicBase
from autofighter.stats import BUS


@dataclass
class ShinyPebble(RelicBase):
    """+3% DEF; first hit grants +3% mitigation for one turn."""

    id: str = "shiny_pebble"
    name: str = "Shiny Pebble"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"defense": 0.03})

    def apply(self, party) -> None:
        super().apply(party)

        triggered: set[int] = set()
        to_remove: dict[int, object] = {}

        def _first_hit(target, attacker, amount) -> None:
            if target not in party.members or id(target) in triggered:
                return
            triggered.add(id(target))
            to_remove[id(target)] = target
            target.mitigation *= 1.03

        def _reset(*_) -> None:
            for key, member in list(to_remove.items()):
                member.mitigation /= 1.03
                to_remove.pop(key, None)

        BUS.subscribe("damage_taken", _first_hit)
        BUS.subscribe("turn_start", _reset)
