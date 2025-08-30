from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.relics._base import RelicBase


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
            survivors = [member for member in party.members if member is not target and member.hp > 0]
            if not survivors:
                return

            stacks = party.relics.count(self.id)

            # Emit relic effect event for ally death buff
            BUS.emit("relic_effect", "tattered_flag", target, "ally_death_buff", 3 * stacks, {
                "fallen_ally": getattr(target, 'id', str(target)),
                "survivors": [getattr(m, 'id', str(m)) for m in survivors],
                "atk_bonus_percentage": 3 * stacks,
                "stacks": stacks
            })

            for member in survivors:
                mod = create_stat_buff(member, name=f"{self.id}_buff", atk_mult=1.03, turns=9999)
                member.effect_manager.add_modifier(mod)

        BUS.subscribe("damage_taken", _fallen)

    def describe(self, stacks: int) -> str:
        if stacks == 1:
            return "+3% party Max HP; ally deaths grant survivors +3% ATK."
        else:
            # Stacks are additive: each copy adds 3%
            total_hp_pct = 3 * stacks
            return f"+{total_hp_pct}% party Max HP ({stacks} stacks, additive); ally deaths grant survivors +3% ATK."
