from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.relics._base import RelicBase
from autofighter.effects import create_stat_buff


@dataclass
class TatteredFlag(RelicBase):
    """+3% party Max HP; ally deaths grant survivors +3% ATK."""

    id: str = "tattered_flag"
    name: str = "Tattered Flag"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"max_hp": 0.03})
    about: str = "+3% party Max HP; ally deaths grant survivors +3% ATK."

    def apply(self, party) -> None:
        super().apply(party)

        def _fallen(target, attacker, amount) -> None:
            if target not in party.members or target.hp > 0:
                return
            for member in party.members:
                if member is not target and member.hp > 0:
                    mod = create_stat_buff(member, name=f"{self.id}_buff", atk_mult=1.03, turns=9999)
                    member.effect_manager.add_modifier(mod)

        BUS.subscribe("damage_taken", _fallen)

    def describe(self, stacks: int) -> str:
        hp = 3 * stacks
        return f"+{hp}% party Max HP; ally deaths grant survivors +3% ATK."
