from dataclasses import dataclass
from dataclasses import field
import importlib
from typing import Callable
from typing import Optional

from plugins.damage_types._base import DamageTypeBase
from plugins.damage_types.generic import Generic
from plugins.event_bus import EventBus

@dataclass
class Stats:
    hp: int = 1000
    max_hp: int = 1000
    exp: int = 0
    level: int = 1
    exp_multiplier: float = 1.0
    actions_per_turn: int = 1

    atk: int = 200
    crit_rate: float = 0.05
    crit_damage: float = 2.0
    effect_hit_rate: float = 1.0
    base_damage_type: DamageTypeBase = field(default_factory=Generic)

    defense: int = 200
    mitigation: float = 1.0
    regain: int = 100
    dodge_odds: float = 0.05
    effect_resistance: float = 0.05

    vitality: float = 1.0
    action_points: int = 0
    damage_taken: int = 0
    damage_dealt: int = 0
    kills: int = 0

    last_damage_taken: int = 0

    passives: list[str] = field(default_factory=list)
    dots: list[str] = field(default_factory=list)
    hots: list[str] = field(default_factory=list)
    damage_types: list[str] = field(default_factory=list)

    def apply_damage(self, amount: int, attacker: Optional["Stats"] = None) -> int:
        def _ensure(obj: "Stats") -> DamageTypeBase:
            dt = getattr(obj, "base_damage_type", Generic())
            if isinstance(dt, str):
                module = importlib.import_module(f"plugins.damage_types.{dt.lower()}")
                dt = getattr(module, dt)()
                obj.base_damage_type = dt
            return dt

        if attacker is not None:
            atk_type = _ensure(attacker)
            atk_type.on_hit(attacker, self)
            amount = atk_type.on_damage(amount, attacker, self)
        self_type = _ensure(self)
        amount = self_type.on_damage_taken(amount, attacker, self)
        amount = self_type.on_party_damage_taken(amount, attacker, self)
        amount = int(amount)
        self.last_damage_taken = amount
        self.damage_taken += amount
        self.hp = max(self.hp - amount, 0)
        BUS.emit("damage_taken", self, attacker, amount)
        if attacker is not None:
            attacker.damage_dealt += amount
            BUS.emit("damage_dealt", attacker, self, amount)
        return amount

    def apply_healing(self, amount: int, healer: Optional["Stats"] = None) -> int:
        def _ensure(obj: "Stats") -> DamageTypeBase:
            dt = getattr(obj, "base_damage_type", Generic())
            if isinstance(dt, str):
                module = importlib.import_module(f"plugins.damage_types.{dt.lower()}")
                dt = getattr(module, dt)()
                obj.base_damage_type = dt
            return dt

        if healer is not None:
            heal_type = _ensure(healer)
            amount = heal_type.on_heal(amount, healer, self)
        self_type = _ensure(self)
        amount = self_type.on_heal_received(amount, healer, self)
        amount = int(amount)
        self.hp = min(self.hp + amount, self.max_hp)
        BUS.emit("heal_received", self, healer, amount)
        if healer is not None:
            BUS.emit("heal", healer, self, amount)
        return amount


StatusHook = Callable[["Stats"], None]
STATUS_HOOKS: list[StatusHook] = []
BUS = EventBus()


def add_status_hook(hook: StatusHook) -> None:
    STATUS_HOOKS.append(hook)


def apply_status_hooks(stats: "Stats") -> None:
    for hook in STATUS_HOOKS:
        hook(stats)
