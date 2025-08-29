import asyncio
from dataclasses import dataclass
from typing import ClassVar

from autofighter.effects import DamageOverTime
from autofighter.stats import BUS
from plugins import damage_effects
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Wind(DamageTypeBase):
    id: str = "Wind"
    weakness: str = "Lightning"
    color: tuple[int, int, int] = (0, 255, 0)

    _players: ClassVar[list] = []
    _foes: ClassVar[list] = []
    _pending: ClassVar[dict[int, list]] = {}
    _subs_registered: ClassVar[bool] = False

    def __post_init__(self) -> None:
        cls = type(self)
        if not cls._subs_registered:
            BUS.subscribe("battle_start", cls._battle_start)
            BUS.subscribe("battle_end", cls._battle_end)
            BUS.subscribe("ultimate_used", cls._ultimate_used)
            BUS.subscribe("hit_landed", cls._hit_landed)
            cls._subs_registered = True

    @classmethod
    def _battle_start(cls, entity) -> None:
        kind = getattr(entity, "plugin_type", "")
        if kind == "player":
            cls._players.append(entity)
        elif kind == "foe":
            cls._foes.append(entity)

    @classmethod
    def _battle_end(cls, entity) -> None:
        if entity in cls._players:
            cls._players.remove(entity)
        if entity in cls._foes:
            cls._foes.remove(entity)
        cls._pending.pop(entity, None)

    @classmethod
    def _ultimate_used(cls, user) -> None:
        if not isinstance(getattr(user, "damage_type", None), cls):
            return
        enemies = cls._foes if getattr(user, "plugin_type", "") == "player" else cls._players
        cls._pending[id(user)] = [e for e in enemies if e.hp > 0 and e is not user]

    @classmethod
    def _hit_landed(cls, attacker, target, *_args) -> None:
        enemies = cls._pending.pop(id(attacker), None)
        if not enemies:
            return
        for enemy in enemies:
            mgr = getattr(enemy, "effect_manager", None)
            if mgr is None:
                continue
            for dot in list(mgr.dots):
                mgr.dots.remove(dot)
                try:
                    enemy.dots.remove(dot.id)
                except ValueError:
                    pass
                asyncio.create_task(dot.tick(target))

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return damage_effects.create_dot(self.id, damage, source)
