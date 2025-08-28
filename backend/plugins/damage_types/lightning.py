import asyncio
from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins import damage_effects
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Lightning(DamageTypeBase):
    id: str = "Lightning"
    weakness: str = "Wind"
    color: tuple[int, int, int] = (255, 255, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return damage_effects.create_dot(self.id, damage, source)

    def on_hit(self, attacker, target) -> None:
        mgr = getattr(target, "effect_manager", None)
        if mgr is None:
            return
        for effect in list(mgr.dots):
            dmg = int(effect.damage * 0.25)
            if dmg > 0:
                asyncio.create_task(target.apply_damage(dmg, attacker=attacker))
