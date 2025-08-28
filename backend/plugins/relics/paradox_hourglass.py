"""Paradox Hourglass relic effects."""

from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.relics._base import RelicBase


@dataclass
class ParadoxHourglass(RelicBase):
    """Can sacrifice allies at battle start to supercharge survivors and debuff foes."""

    id: str = "paradox_hourglass"
    name: str = "Paradox Hourglass"
    stars: int = 5
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 2.0, "defense": 2.0})
    about: str = (
        "At battle start may sacrifice allies to supercharge survivors and shred foe defense."
    )

    def apply(self, party) -> None:
        """On battle start possibly sacrifices allies for massive buffs."""
        super().apply(party)

        stacks = party.relics.count(self.id)
        state: dict[str, dict] = {"buffs": {}, "foe": {}}

        def _battle_start(entity) -> None:
            from plugins.foes._base import FoeBase

            if isinstance(entity, FoeBase):
                base_def = entity.defense
                div = 4 + (stacks - 1)
                new_def = max(100, int(base_def / div))
                mod = create_stat_buff(
                    entity,
                    name=f"{self.id}_foe_{id(entity)}",
                    defense=new_def - base_def,
                    turns=9999,
                )
                entity.effect_manager.add_modifier(mod)
                state["foe"][id(entity)] = mod
                return

            if state.get("done"):
                return
            state["done"] = True

            alive = [m for m in party.members if m.hp > 0]
            if len(alive) <= 1:
                return
            chance = 0.6 * (len(alive) - 1) / len(alive)
            if random.random() >= chance:
                return
            kill_count = min(stacks, 4, len(alive) - 1)
            to_kill = random.sample(alive, kill_count)
            for m in to_kill:
                m.hp = 0
            survivors = [m for m in party.members if m.hp > 0]
            mult = 3 + (stacks - 1)
            for m in survivors:
                mod = create_stat_buff(
                    m,
                    name=f"{self.id}_ally_{id(m)}",
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
                m.effect_manager.add_modifier(mod)
                m.hp = m.max_hp
                state["buffs"][id(m)] = mod

        def _battle_end(entity) -> None:
            from plugins.foes._base import FoeBase

            if isinstance(entity, FoeBase):
                mod = state["foe"].pop(id(entity), None)
                if mod:
                    mod.remove()
                    if mod in entity.effect_manager.mods:
                        entity.effect_manager.mods.remove(mod)
                    if mod.id in entity.mods:
                        entity.mods.remove(mod.id)
                return

            for member in party.members:
                mod = state["buffs"].pop(id(member), None)
                if mod:
                    mod.remove()
                    if mod in member.effect_manager.mods:
                        member.effect_manager.mods.remove(mod)
                    if mod.id in member.mods:
                        member.mods.remove(mod.id)
            state.pop("done", None)

        BUS.subscribe("battle_start", _battle_start)
        BUS.subscribe("battle_end", _battle_end)

    def describe(self, stacks: int) -> str:
        div = 4 + (stacks - 1)
        mult = 3 + (stacks - 1)
        kill = min(stacks, 4)
        return (
            f"60% chance to sacrifice up to {kill} random allies (max 4). "
            f"Survivors gain {mult}x stats and foes' DEF is divided by {div}."
        )
