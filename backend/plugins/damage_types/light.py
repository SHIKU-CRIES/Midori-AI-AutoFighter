from dataclasses import dataclass
from autofighter.effects import DamageOverTime
from plugins import damage_effects
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Light(DamageTypeBase):
    id: str = "Light"
    weakness: str = "Dark"
    color: tuple[int, int, int] = (255, 255, 255)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return damage_effects.create_dot(self.id, damage, source)

    async def on_action(self, actor, allies, enemies):
        for ally in allies:
            mgr = getattr(ally, "effect_manager", None)
            if mgr is not None:
                hot = damage_effects.create_hot(self.id, actor)
                if hot is not None:
                    mgr.add_hot(hot)
        for ally in allies:
            if ally.hp > 0 and ally.hp / ally.max_hp < 0.25:
                await ally.apply_healing(actor.atk, healer=actor)
                return False
        return True
