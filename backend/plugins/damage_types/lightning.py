import asyncio
from typing import TYPE_CHECKING
from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase

if TYPE_CHECKING:
    from plugins.dots.charged_decay import ChargedDecay


@dataclass
class Lightning(DamageTypeBase):
    id: str = "Lightning"
    weakness: str = "Wind"
    color: tuple[int, int, int] = (255, 255, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        from plugins.dots.charged_decay import ChargedDecay

        dot = ChargedDecay(int(damage * 0.25), 3)
        dot.source = source
        return dot

    def on_hit(self, attacker, target) -> None:
        mgr = getattr(target, "effect_manager", None)
        if mgr is None:
            return
        for effect in list(mgr.dots):
            dmg = int(effect.damage * 0.25)
            if dmg > 0:
                asyncio.create_task(target.apply_damage(dmg, attacker=attacker))
