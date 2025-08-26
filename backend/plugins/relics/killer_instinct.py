from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.relics._base import RelicBase
from plugins.players._base import PlayerBase
from autofighter.effects import create_stat_buff


@dataclass
class KillerInstinct(RelicBase):
    """Ultimates grant +75% ATK for the turn; kills grant another turn."""

    id: str = "killer_instinct"
    name: str = "Killer Instinct"
    stars: int = 2
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "Ultimates grant +75% ATK for the turn; kills grant another turn."

    def apply(self, party) -> None:
        super().apply(party)

        buffs: dict[int, tuple[PlayerBase, object]] = {}

        def _ultimate(user) -> None:
            mod = create_stat_buff(user, name=f"{self.id}_atk", atk_mult=1.75, turns=1)
            user.effect_manager.add_modifier(mod)
            buffs[id(user)] = (user, mod)

        def _damage(target, attacker, amount) -> None:
            if target.hp <= 0 and id(attacker) in buffs:
                BUS.emit("extra_turn", attacker)

        def _turn_end() -> None:
            for _, (member, mod) in list(buffs.items()):
                mod.remove()
                if mod in member.effect_manager.mods:
                    member.effect_manager.mods.remove(mod)
                if mod.id in member.mods:
                    member.mods.remove(mod.id)
            buffs.clear()

        BUS.subscribe("ultimate_used", _ultimate)
        BUS.subscribe("damage_taken", _damage)
        BUS.subscribe("turn_end", lambda: _turn_end())

    def describe(self, stacks: int) -> str:
        pct = 75 * stacks
        return f"Ultimates grant +{pct}% ATK for the turn; kills grant another turn."
