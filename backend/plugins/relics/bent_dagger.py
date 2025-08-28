from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.relics._base import RelicBase


@dataclass
class BentDagger(RelicBase):
    """+3% ATK; killing a foe grants +1% ATK for the rest of combat."""

    id: str = "bent_dagger"
    name: str = "Bent Dagger"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 0.03})
    about: str = "+3% ATK; killing a foe grants +1% ATK for the rest of combat."

    def apply(self, party) -> None:
        super().apply(party)

        def _on_death(target, attacker, amount) -> None:
            if target in party.members or target.hp > 0:
                return
            for member in party.members:
                mod = create_stat_buff(member, name=f"{self.id}_kill", atk_mult=1.01, turns=9999)
                member.effect_manager.add_modifier(mod)

        BUS.subscribe("damage_taken", _on_death)

    def describe(self, stacks: int) -> str:
        if stacks == 1:
            return "+3% ATK; killing a foe grants +1% ATK for the rest of combat."
        else:
            # Calculate actual multiplicative bonus: (1.03)^stacks - 1
            multiplier = (1.03 ** stacks) - 1
            total_pct = round(multiplier * 100, 2)
            return f"+{total_pct}% ATK ({stacks} stacks, multiplicative); killing a foe grants +1% ATK for the rest of combat."
