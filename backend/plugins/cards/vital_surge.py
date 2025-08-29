from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import EffectManager
from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class VitalSurge(CardBase):
    id: str = "vital_surge"
    name: str = "Vital Surge"
    stars: int = 2
    effects: dict[str, float] = field(default_factory=lambda: {"max_hp": 0.55})
    about: str = "+55% Max HP; below 50% HP, gain +55% ATK."

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)
        active: dict[int, object] = {}

        def _check(member) -> None:
            pid = id(member)
            mgr = getattr(member, "effect_manager", None)
            if mgr is None:
                mgr = EffectManager(member)
                member.effect_manager = mgr
            if member.hp <= member.max_hp / 2:
                if pid in active:
                    return
                mod = create_stat_buff(
                    member,
                    name=f"{self.id}_atk",
                    turns=9999,
                    atk_mult=1.55,
                )
                active[pid] = mod
                mgr.add_modifier(mod)
                BUS.emit(
                    "card_effect",
                    self.id,
                    member,
                    "low_hp_atk",
                    55,
                    {},
                )
            else:
                mod = active.pop(pid, None)
                if mod is not None:
                    mod.remove()
                    if hasattr(mgr, "mods") and mod in mgr.mods:
                        mgr.mods.remove(mod)
                    if hasattr(member, "mods") and mod.id in member.mods:
                        member.mods.remove(mod.id)

        def _turn_start() -> None:
            for m in party.members:
                _check(m)

        def _damage_taken(victim, *_args) -> None:
            if victim in party.members:
                _check(victim)

        def _heal_received(member, *_args) -> None:
            if member in party.members:
                _check(member)

        BUS.subscribe("turn_start", _turn_start)
        BUS.subscribe("damage_taken", _damage_taken)
        BUS.subscribe("heal_received", _heal_received)
