import asyncio
from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.effects.aftertaste import Aftertaste
from plugins.relics._base import RelicBase


@dataclass
class FrostSigil(RelicBase):
    """Hits apply chill dealing 5% ATK as Aftertaste; each stack adds a hit."""

    id: str = "frost_sigil"
    name: str = "Frost Sigil"
    stars: int = 2
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "Hits apply chill dealing 5% ATK as Aftertaste; each stack adds a hit."

    def apply(self, party) -> None:
        super().apply(party)

        state = getattr(party, "_frost_sigil_state", None)
        if state is None:
            party._frost_sigil_state = True

            def _hit(attacker, target, amount, source_type="attack", source_name=None) -> None:
                stacks = party.relics.count(self.id)
                dmg = int(attacker.atk * 0.05)

                # Track frost sigil application
                BUS.emit("relic_effect", "frost_sigil", attacker, "chill_applied", dmg, {
                    "target": getattr(target, 'id', str(target)),
                    "aftertaste_hits": stacks,
                    "damage_per_hit": dmg,
                    "atk_percentage": 5,
                    "attacker_atk": attacker.atk,
                    "trigger": "hit_landed"
                })

                asyncio.create_task(
                    Aftertaste(base_pot=dmg, hits=stacks).apply(attacker, target)
                )

            BUS.subscribe("hit_landed", _hit)

    def describe(self, stacks: int) -> str:
        hit_word = "hit" if stacks == 1 else "hits"
        return f"Hits apply chill dealing 5% ATK as Aftertaste {stacks} {hit_word}."
