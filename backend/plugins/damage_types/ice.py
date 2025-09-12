import asyncio
from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from autofighter.stats import Stats
from plugins import damage_effects
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Ice(DamageTypeBase):
    """Control element that chills foes and slows their actions."""
    id: str = "Ice"
    weakness: str = "Fire"
    color: tuple[int, int, int] = (0, 255, 255)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return damage_effects.create_dot(self.id, damage, source)

    async def ultimate(self, user: Stats, foes: list[Stats]) -> bool:
        """Strike all foes six times, ramping damage by 30% per target."""
        if not getattr(user, "use_ultimate", lambda: False)():
            return False
        base = user.atk
        for _ in range(6):
            bonus = 1.0
            for foe in foes:
                dmg = int(base * bonus)
                await foe.apply_damage(dmg, attacker=user, action_name="Ice Ultimate")
                await asyncio.sleep(0.002)
                bonus += 0.3
            await asyncio.sleep(0.002)
        return True

    @classmethod
    def get_ultimate_description(cls) -> str:
        return (
            "Strikes all foes six times in succession. Each hit within a wave "
            "deals 30% more damage than the previous target."
        )
