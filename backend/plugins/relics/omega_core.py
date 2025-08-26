"""Omega Core relic effects."""

import asyncio

from dataclasses import field
from dataclasses import dataclass

from autofighter.stats import BUS
from autofighter.effects import create_stat_buff
from plugins.relics._base import RelicBase


@dataclass
class OmegaCore(RelicBase):
    """Huge stat surge for a short time, then escalating HP drain."""

    id: str = "omega_core"
    name: str = "Omega Core"
    stars: int = 5
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 5.0, "defense": 5.0})
    about: str = (
        "Multiplies all stats for a short time before draining ally health."
    )

    def apply(self, party) -> None:
        """Burst of power followed by increasing HP drain."""
        super().apply(party)

        stacks = party.relics.count(self.id)
        delay = 10 + 2 * (stacks - 1)
        mult = 6.0 + (stacks - 1)
        state = {"mods": {}, "turn": 0}

        def _battle_start(entity) -> None:
            from plugins.foes._base import FoeBase

            if isinstance(entity, FoeBase) or state["mods"]:
                return
            for member in party.members:
                mod = create_stat_buff(
                    member,
                    name=f"{self.id}_{id(member)}",
                    turns=9999,
                    atk_mult=mult,
                    defense_mult=mult,
                    max_hp_mult=mult,
                    hp_mult=mult,
                    crit_rate_mult=mult,
                    crit_damage_mult=mult,
                    effect_hit_rate_mult=mult,
                    effect_resistance_mult=mult,
                    vitality_mult=mult,
                    mitigation_mult=mult,
                )
                member.effect_manager.add_modifier(mod)
                asyncio.create_task(member.apply_healing(member.max_hp))
                state["mods"][id(member)] = mod
            state["turn"] = 0

        def _turn_start() -> None:
            if not state["mods"]:
                return
            state["turn"] += 1
            if state["turn"] <= delay:
                return
            drain = (state["turn"] - delay) * 0.01
            for member in party.members:
                dmg = int(member.max_hp * drain)
                asyncio.create_task(member.apply_damage(dmg))

        def _battle_end(entity) -> None:
            from plugins.foes._base import FoeBase

            if not isinstance(entity, FoeBase):
                return
            for member in party.members:
                mod = state["mods"].pop(id(member), None)
                if mod:
                    mod.remove()
                    if mod in member.effect_manager.mods:
                        member.effect_manager.mods.remove(mod)
                    if mod.id in member.mods:
                        member.mods.remove(mod.id)
            state["mods"].clear()

        BUS.subscribe("battle_start", _battle_start)
        BUS.subscribe("turn_start", _turn_start)
        BUS.subscribe("battle_end", _battle_end)

    def describe(self, stacks: int) -> str:
        delay = 10 + 2 * (stacks - 1)
        mult = 6 + (stacks - 1)
        return (
            f"Boosts all ally stats by {mult}x for the entire fight. "
            f"After {delay} turns, allies lose an extra 1% of Max HP each turn."
        )
