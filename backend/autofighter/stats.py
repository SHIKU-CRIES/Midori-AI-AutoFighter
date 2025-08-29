from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
import importlib
import logging
import random
from typing import Dict
from typing import Optional
from typing import Union

from plugins.damage_types._base import DamageTypeBase
from plugins.damage_types.generic import Generic
from plugins.event_bus import EventBus

log = logging.getLogger(__name__)

# Global enrage percentage applied during battles.
# Set by battle rooms when enrage is active, used in damage/heal calculations.
_ENRAGE_PERCENT: float = 0.0
_BATTLE_ACTIVE: bool = False


@dataclass
class StatEffect:
    """Represents a temporary effect that modifies stats."""
    name: str
    stat_modifiers: Dict[str, Union[int, float]]  # stat_name -> modifier value
    duration: int = -1  # -1 for permanent effects (cards/relics), >0 for temporary
    source: str = "unknown"  # source identifier (card name, relic name, etc.)

    def is_expired(self) -> bool:
        """Check if this effect has expired."""
        return self.duration == 0

    def tick(self) -> None:
        """Reduce duration by 1 if it's a temporary effect."""
        if self.duration > 0:
            self.duration -= 1


def set_enrage_percent(value: float) -> None:
    """Set global enrage percent (e.g., 0.15 for +15% damage taken, -15% healing).

    This is applied uniformly to all entities during damage/heal resolution.
    """
    global _ENRAGE_PERCENT
    try:
        _ENRAGE_PERCENT = max(float(value), 0.0)
    except Exception:
        _ENRAGE_PERCENT = 0.0


def get_enrage_percent() -> float:
    return _ENRAGE_PERCENT


def set_battle_active(active: bool) -> None:
    """Mark whether a battle is currently active.

    Used to ignore stray async damage/heal pings after battles conclude,
    preventing post-battle loops from background tasks.
    """
    global _BATTLE_ACTIVE
    try:
        _BATTLE_ACTIVE = bool(active)
    except Exception:
        _BATTLE_ACTIVE = False


def is_battle_active() -> bool:
    return _BATTLE_ACTIVE

@dataclass
class Stats:
    # Core progression stats
    hp: int = 1000
    exp: int = 0
    level: int = 1
    exp_multiplier: float = 1.0
    actions_per_turn: int = 1

    # Base stats (immutable during battle, only change on level up or permanent upgrades)
    _base_max_hp: int = field(default=1000, init=False)
    _base_atk: int = field(default=200, init=False)
    _base_defense: int = field(default=200, init=False)
    _base_crit_rate: float = field(default=0.05, init=False)
    _base_crit_damage: float = field(default=2.0, init=False)
    _base_effect_hit_rate: float = field(default=1.0, init=False)
    _base_mitigation: float = field(default=1.0, init=False)
    _base_regain: int = field(default=100, init=False)
    _base_dodge_odds: float = field(default=0.05, init=False)
    _base_effect_resistance: float = field(default=0.05, init=False)
    _base_vitality: float = field(default=1.0, init=False)

    # Damage type and other permanent attributes
    damage_type: DamageTypeBase = field(default_factory=Generic)

    # Runtime tracking stats (not affected by effects)
    action_points: int = 0
    damage_taken: int = 0
    damage_dealt: int = 0
    kills: int = 0
    last_damage_taken: int = 0

    # Ultimate system
    ultimate_charge: int = 0
    ultimate_ready: bool = False

    # Overheal system (for shields from relics/cards)
    overheal_enabled: bool = field(default=False, init=False)
    shields: int = field(default=0, init=False)  # Amount of overheal/shields

    # Collections
    passives: list[str] = field(default_factory=list)
    dots: list[str] = field(default_factory=list)
    hots: list[str] = field(default_factory=list)
    mods: list[str] = field(default_factory=list)

    # Effects system
    _active_effects: list[StatEffect] = field(default_factory=list, init=False)

    level_up_gains: dict[str, int] = field(
        default_factory=lambda: {"max_hp": 10, "atk": 5, "defense": 3}
    )

    def __post_init__(self):
        """Initialize base stats from constructor values."""
        # Initialize base stats with default values if not already set
        if not hasattr(self, '_base_max_hp') or self._base_max_hp == 0:
            self._base_max_hp = 1000
        if not hasattr(self, '_base_atk') or self._base_atk == 0:
            self._base_atk = 200
        if not hasattr(self, '_base_defense') or self._base_defense == 0:
            self._base_defense = 200
        if not hasattr(self, '_base_crit_rate'):
            self._base_crit_rate = 0.05
        if not hasattr(self, '_base_crit_damage'):
            self._base_crit_damage = 2.0
        if not hasattr(self, '_base_effect_hit_rate'):
            self._base_effect_hit_rate = 1.0
        if not hasattr(self, '_base_mitigation'):
            self._base_mitigation = 1.0
        if not hasattr(self, '_base_regain'):
            self._base_regain = 100
        if not hasattr(self, '_base_dodge_odds'):
            self._base_dodge_odds = 0.05
        if not hasattr(self, '_base_effect_resistance'):
            self._base_effect_resistance = 0.05
        if not hasattr(self, '_base_vitality'):
            self._base_vitality = 1.0

        # Set hp to match max_hp at start
        self.hp = self.max_hp

    # Runtime stat properties (base stats + effects)
    @property
    def max_hp(self) -> int:
        """Calculate runtime max HP (base + effects)."""
        return int(self._base_max_hp + self._calculate_stat_modifier('max_hp'))

    @property
    def atk(self) -> int:
        """Calculate runtime attack (base + effects)."""
        return int(self._base_atk + self._calculate_stat_modifier('atk'))

    @property
    def defense(self) -> int:
        """Calculate runtime defense (base + effects)."""
        return int(self._base_defense + self._calculate_stat_modifier('defense'))

    @property
    def crit_rate(self) -> float:
        """Calculate runtime crit rate (base + effects)."""
        return max(0.0, self._base_crit_rate + self._calculate_stat_modifier('crit_rate'))

    @property
    def crit_damage(self) -> float:
        """Calculate runtime crit damage (base + effects)."""
        return max(1.0, self._base_crit_damage + self._calculate_stat_modifier('crit_damage'))

    @property
    def effect_hit_rate(self) -> float:
        """Calculate runtime effect hit rate (base + effects)."""
        return max(0.0, self._base_effect_hit_rate + self._calculate_stat_modifier('effect_hit_rate'))

    @property
    def mitigation(self) -> float:
        """Calculate runtime mitigation (base + effects)."""
        return max(0.1, self._base_mitigation + self._calculate_stat_modifier('mitigation'))

    @mitigation.setter
    def mitigation(self, value: float) -> None:  # type: ignore[override]
        try:
            self._base_mitigation = float(value)
        except Exception:
            # Fallback to no-op on invalid values
            pass

    @property
    def regain(self) -> int:
        """Calculate runtime regain (base + effects)."""
        return int(max(0, self._base_regain + self._calculate_stat_modifier('regain')))

    @property
    def dodge_odds(self) -> float:
        """Calculate runtime dodge odds (base + effects)."""
        return max(0.0, min(1.0, self._base_dodge_odds + self._calculate_stat_modifier('dodge_odds')))

    @property
    def effect_resistance(self) -> float:
        """Calculate runtime effect resistance (base + effects)."""
        return max(0.0, self._base_effect_resistance + self._calculate_stat_modifier('effect_resistance'))

    @property
    def vitality(self) -> float:
        """Calculate runtime vitality (base + effects)."""
        return max(0.01, self._base_vitality + self._calculate_stat_modifier('vitality'))

    @vitality.setter
    def vitality(self, value: float) -> None:  # type: ignore[override]
        try:
            self._base_vitality = float(value)
        except Exception:
            pass

    def _calculate_stat_modifier(self, stat_name: str) -> Union[int, float]:
        """Calculate the total modifier for a stat from all active effects."""
        total = 0
        for effect in self._active_effects:
            if stat_name in effect.stat_modifiers:
                total += effect.stat_modifiers[stat_name]
        return total

    # Base stat access methods (for permanent changes like leveling)
    def set_base_stat(self, stat_name: str, value: Union[int, float]) -> None:
        """Set a base stat value (use only for permanent changes like leveling)."""
        base_attr = f"_base_{stat_name}"
        if hasattr(self, base_attr):
            setattr(self, base_attr, value)
        else:
            log.warning(f"Attempted to set unknown base stat: {stat_name}")

    def get_base_stat(self, stat_name: str) -> Union[int, float]:
        """Get a base stat value."""
        base_attr = f"_base_{stat_name}"
        if hasattr(self, base_attr):
            return getattr(self, base_attr)
        return 0

    def modify_base_stat(self, stat_name: str, amount: Union[int, float]) -> None:
        """Modify a base stat (use only for permanent changes like leveling)."""
        current = self.get_base_stat(stat_name)
        self.set_base_stat(stat_name, current + amount)

    # Effect management methods
    def add_effect(self, effect: StatEffect) -> None:
        """Add a stat effect."""
        # Remove any existing effect with the same name to prevent stacking
        self.remove_effect_by_name(effect.name)
        self._active_effects.append(effect)
        log.debug(f"Added effect {effect.name} with modifiers {effect.stat_modifiers}")

    def remove_effect_by_name(self, effect_name: str) -> bool:
        """Remove an effect by name. Returns True if an effect was removed."""
        initial_count = len(self._active_effects)
        self._active_effects = [e for e in self._active_effects if e.name != effect_name]
        removed = len(self._active_effects) < initial_count
        if removed:
            log.debug(f"Removed effect {effect_name}")
        return removed

    def remove_effect_by_source(self, source: str) -> int:
        """Remove all effects from a specific source. Returns number of effects removed."""
        initial_count = len(self._active_effects)
        self._active_effects = [e for e in self._active_effects if e.source != source]
        removed_count = initial_count - len(self._active_effects)
        if removed_count > 0:
            log.debug(f"Removed {removed_count} effects from source {source}")
        return removed_count

    def tick_effects(self) -> None:
        """Update all temporary effects, removing expired ones."""
        expired_effects = []
        for effect in self._active_effects:
            effect.tick()
            if effect.is_expired():
                expired_effects.append(effect.name)

        for effect_name in expired_effects:
            self.remove_effect_by_name(effect_name)

    def get_active_effects(self) -> list[StatEffect]:
        """Get a copy of all active effects."""
        return self._active_effects.copy()

    def clear_all_effects(self) -> None:
        """Remove all active effects."""
        self._active_effects.clear()
        log.debug("Cleared all stat effects")

    @property
    def element_id(self) -> str:
        dt = getattr(self, "damage_type", Generic())
        if isinstance(dt, str):
            return dt
        ident = getattr(dt, "id", None) or getattr(dt, "name", None)
        return str(ident or dt)

    def exp_to_level(self) -> int:
        return (2 ** self.level) * 50

    async def maybe_regain(self, turn: int) -> None:
        if turn % 2 != 0:
            return
        bonus = max(self.regain - 100, 0) * 0.00005
        percent = 0.01 + bonus
        heal = int(self.max_hp * percent)
        await self.apply_healing(heal)

    def _on_level_up(self) -> None:
        inc = random.uniform(0.003 * self.level, 0.008 * self.level)

        # Apply percentage increase to base stats
        base_stat_names = ['max_hp', 'atk', 'defense', 'crit_rate', 'crit_damage',
                          'effect_hit_rate', 'mitigation', 'regain', 'dodge_odds',
                          'effect_resistance', 'vitality']

        for stat_name in base_stat_names:
            current_base = self.get_base_stat(stat_name)
            if isinstance(current_base, (int, float)) and current_base > 0:
                new_val = current_base * (1 + inc)
                self.set_base_stat(stat_name, type(current_base)(new_val))

        # Apply fixed gains from level_up_gains to base stats
        for stat, base in self.level_up_gains.items():
            self.modify_base_stat(stat, base * self.level)

        # Set current HP to new max HP
        self.hp = self.max_hp

    def gain_exp(self, amount: int) -> None:
        if self.level < 1000:
            amount *= 10
        self.exp += int(amount * self.exp_multiplier * self.vitality)
        while self.exp >= self.exp_to_level():
            needed = self.exp_to_level()
            self.exp -= needed
            self.level += 1
            self._on_level_up()

    def add_ultimate_charge(self, amount: int = 1) -> None:
        """Increase ultimate charge, capping at 15."""
        if self.ultimate_ready:
            return
        self.ultimate_charge = min(15, self.ultimate_charge + amount)
        if self.ultimate_charge >= 15:
            self.ultimate_ready = True

    def handle_ally_action(self, actor: "Stats") -> None:
        """Grant bonus charge when an ally takes an action."""
        if actor is self:
            return
        dt = getattr(self, "damage_type", None)
        if getattr(dt, "id", "").lower() == "ice":
            self.add_ultimate_charge(actor.actions_per_turn)


    async def apply_damage(
        self,
        amount: float,
        attacker: Optional["Stats"] = None,
        *,
        trigger_on_hit: bool = True,
    ) -> int:
        # Drop any stray post-battle damage tasks to avoid loops.
        from autofighter.stats import is_battle_active  # local import for clarity
        if not is_battle_active():
            return 0
        # If already dead, ignore further damage applications to avoid
        # post-death damage loops from async tasks or event subscribers.
        if getattr(self, "hp", 0) <= 0:
            return 0
        def _ensure(obj: "Stats") -> DamageTypeBase:
            dt = getattr(obj, "damage_type", Generic())
            if isinstance(dt, str):
                module = importlib.import_module(
                    f"plugins.damage_types.{dt.lower()}"
                )
                dt = getattr(module, dt)()
                obj.damage_type = dt
            return dt

        critical = False
        if attacker is not None:
            if random.random() < self.dodge_odds:
                log.info(
                    "%s dodges attack from %s",
                    self.id,
                    getattr(attacker, "id", "unknown"),
                )
                return 0
            atk_type = _ensure(attacker)
            # Avoid recursive chains from secondary effects (e.g., Lightning on-hit reactions)
            if trigger_on_hit:
                atk_type.on_hit(attacker, self)
            if random.random() < attacker.crit_rate:
                critical = True
                amount *= attacker.crit_damage
            amount = atk_type.on_damage(amount, attacker, self)
        self_type = _ensure(self)
        amount = self_type.on_damage_taken(amount, attacker, self)
        amount = self_type.on_party_damage_taken(amount, attacker, self)
        src_vit = attacker.vitality if attacker is not None else 1.0
        # Guard against division by zero if vitality/mitigation are driven to 0 by effects
        defense_term = max(self.defense ** 5, 1)
        vit = float(self.vitality) if isinstance(self.vitality, (int, float)) else 1.0
        mit = float(self.mitigation) if isinstance(self.mitigation, (int, float)) else 1.0
        # Clamp to a tiny positive epsilon to avoid zero/NaN
        EPS = 1e-6
        vit = vit if vit > EPS else EPS
        mit = mit if mit > EPS else EPS
        denom = defense_term * vit * mit
        amount = ((amount ** 2) * src_vit) / denom
        # Enrage: increase damage taken globally by N% per enrage stack
        enr = get_enrage_percent()
        if enr > 0:
            amount *= (1.0 + enr)
        amount = max(int(amount), 1)
        if critical and attacker is not None:
            log.info("Critical hit! %s -> %s for %s", attacker.id, self.id, amount)
        original_amount = amount
        self.last_damage_taken = amount
        self.damage_taken += amount

        # Handle shields/overheal absorption first
        if self.shields > 0:
            shield_absorbed = min(amount, self.shields)
            self.shields -= shield_absorbed
            amount -= shield_absorbed

        # Apply remaining damage to HP
        if amount > 0:
            self.hp = max(self.hp - amount, 0)

        BUS.emit("damage_taken", self, attacker, original_amount)
        if attacker is not None:
            attacker.damage_dealt += original_amount
            BUS.emit("damage_dealt", attacker, self, original_amount)
        return original_amount

    async def apply_healing(self, amount: int, healer: Optional["Stats"] = None) -> int:
        def _ensure(obj: "Stats") -> DamageTypeBase:
            dt = getattr(obj, "damage_type", Generic())
            if isinstance(dt, str):
                module = importlib.import_module(
                    f"plugins.damage_types.{dt.lower()}"
                )
                dt = getattr(module, dt)()
                obj.damage_type = dt
            return dt

        if healer is not None:
            heal_type = _ensure(healer)
            amount = heal_type.on_heal(amount, healer, self)
        self_type = _ensure(self)
        amount = self_type.on_heal_received(amount, healer, self)
        src_vit = healer.vitality if healer is not None else 1.0
        # Healing is amplified by both source and target vitality
        amount = amount * src_vit * self.vitality
        # Enrage: reduce healing output globally by N% per enrage stack
        enr = get_enrage_percent()
        if enr > 0:
            amount *= max(1.0 - enr, 0.0)
        amount = int(amount)

        # Handle overheal/shields if enabled
        if self.overheal_enabled:
            if self.hp < self.max_hp:
                # Heal normal HP first
                normal_heal = min(amount, self.max_hp - self.hp)
                self.hp += normal_heal
                amount -= normal_heal

            # Add any remaining healing as shields with diminishing returns
            if amount > 0:
                # Calculate penalty based on CURRENT shield amount
                current_overheal_percent = (self.shields / self.max_hp) * 100

                if current_overheal_percent <= 0:
                    # No existing overheal - healing works normally
                    self.shields += amount
                else:
                    # Apply diminishing returns based on current overheal percentage
                    # At 10% overheal, healing effectiveness = 1/5 = 0.2
                    # So 10 healing gives 2 shields, matching the example
                    healing_effectiveness = 1.0 / 5.0  # 20% effectiveness when overhealed
                    shields_to_add = amount * healing_effectiveness
                    self.shields += int(shields_to_add)
        else:
            # Standard healing - cap at max HP
            self.hp = min(self.hp + amount, self.max_hp)

        BUS.emit("heal_received", self, healer, amount)
        if healer is not None:
            BUS.emit("heal", healer, self, amount)
        return amount

    def enable_overheal(self) -> None:
        """Enable overheal/shields for this entity (typically from relic/card effects)."""
        self.overheal_enabled = True

    def disable_overheal(self) -> None:
        """Disable overheal/shields and remove any existing shields."""
        self.overheal_enabled = False
        self.shields = 0

    @property
    def effective_hp(self) -> int:
        """Get total effective HP (actual HP + shields)."""
        return self.hp + self.shields


StatusHook = Callable[["Stats"], None]
STATUS_HOOKS: list[StatusHook] = []
BUS = EventBus()

def _log_damage_taken(
    target: "Stats", attacker: Optional["Stats"], amount: int
) -> None:
    attacker_id = getattr(attacker, "id", "unknown")
    log.info("%s takes %s from %s", target.id, amount, attacker_id)


def _log_heal_received(
    target: "Stats", healer: Optional["Stats"], amount: int
) -> None:
    healer_id = getattr(healer, "id", "unknown")
    log.info("%s heals %s from %s", target.id, amount, healer_id)


BUS.subscribe("damage_taken", _log_damage_taken)
BUS.subscribe("heal_received", _log_heal_received)


def add_status_hook(hook: StatusHook) -> None:
    STATUS_HOOKS.append(hook)


def apply_status_hooks(stats: "Stats") -> None:
    for hook in STATUS_HOOKS:
        hook(stats)
