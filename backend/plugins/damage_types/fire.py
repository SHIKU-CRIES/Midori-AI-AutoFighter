import asyncio
from dataclasses import dataclass
import math

from autofighter.effects import DamageOverTime
from autofighter.stats import BUS
from autofighter.stats import Stats
from plugins import damage_effects
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Fire(DamageTypeBase):
    id: str = "Fire"
    weakness: str = "Ice"
    color: tuple[int, int, int] = (255, 0, 0)

    _drain_stacks: int = 0

    def __post_init__(self) -> None:
        BUS.subscribe("ultimate_used", self._on_ultimate_used)
        BUS.subscribe("turn_start", self._on_turn_start)
        BUS.subscribe("battle_end", self._on_battle_end)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return damage_effects.create_dot(self.id, damage, source)

    def on_damage(self, damage: float, attacker: Stats, target: Stats) -> float:
        if attacker.max_hp <= 0:
            return damage
        missing_ratio = 1 - (attacker.hp / attacker.max_hp)
        dmg = damage * (1 + missing_ratio)
        if self._drain_stacks > 0:
            dmg *= math.sqrt(5)
        return dmg

    async def ultimate(self, actor, allies, enemies) -> bool:
        """Fire ultimate: Deal massive damage to all enemies, scaling with missing HP."""
        if not getattr(actor, "use_ultimate", lambda: False)():
            return False

        if not enemies:
            return False

        # Fire ultimate damage scales with the caster's missing HP
        missing_ratio = 1 - (actor.hp / max(actor.max_hp, 1))
        base_damage = int(getattr(actor, "atk", 0))
        ult_damage = int(base_damage * (1.5 + missing_ratio))

        for enemy in enemies:
            if getattr(enemy, "hp", 0) <= 0:
                continue

            # Deal fire ultimate damage
            await enemy.apply_damage(ult_damage, attacker=actor, action_name="Fire Ultimate")

        return True

    def _on_ultimate_used(self, user: Stats) -> None:
        if getattr(user, "damage_type", None) is not self:
            return
        self._drain_stacks += 1

    def _on_turn_start(self, actor: Stats) -> None:
        if self._drain_stacks <= 0:
            return
        if getattr(actor, "damage_type", None) is not self:
            return
        dmg = actor.max_hp * 0.05 * self._drain_stacks
        if dmg > 0:
            pre = math.sqrt(dmg)
            asyncio.create_task(actor.apply_damage(pre))

    def _on_battle_end(self, *_: object) -> None:
        self._drain_stacks = 0
