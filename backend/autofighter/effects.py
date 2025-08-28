import asyncio
from dataclasses import dataclass
from dataclasses import field
import random
from typing import Optional

from rich.console import Console

from autofighter.stats import StatEffect
from autofighter.stats import Stats


@dataclass
class StatModifier:
    """Temporarily adjust stats via additive or multiplicative changes using the new StatEffect system."""

    stats: Stats
    name: str
    turns: int
    id: str
    deltas: dict[str, float] | None = None
    multipliers: dict[str, float] | None = None
    _effect_applied: bool = field(init=False, default=False)

    def apply(self) -> None:
        """Apply configured modifiers to the stats object using StatEffect."""
        if self._effect_applied:
            return  # Already applied

        # Convert deltas and multipliers to a single stat_modifiers dict
        stat_modifiers = {}

        # Handle additive deltas
        for name, value in (self.deltas or {}).items():
            stat_modifiers[name] = stat_modifiers.get(name, 0) + value

        # Handle multiplicative changes by converting to additive
        # Note: This is an approximation since pure multiplicative requires more complex handling
        for name, multiplier in (self.multipliers or {}).items():
            if hasattr(self.stats, name):
                # Get base stat value for calculation
                if hasattr(self.stats, 'get_base_stat'):
                    base_value = self.stats.get_base_stat(name)
                else:
                    base_value = getattr(self.stats, name, 0)

                # Convert multiplier to additive value
                additive_change = base_value * (multiplier - 1.0)
                stat_modifiers[name] = stat_modifiers.get(name, 0) + additive_change

        if stat_modifiers:
            # Create and apply StatEffect
            effect = StatEffect(
                name=self.id,
                stat_modifiers=stat_modifiers,
                duration=self.turns if self.turns > 0 else -1,  # -1 for permanent
                source=f"modifier_{self.name}"
            )

            self.stats.add_effect(effect)
            self._effect_applied = True

    def remove(self) -> None:
        """Remove the effect from stats if it was applied."""
        if self._effect_applied:
            self.stats.remove_effect_by_name(self.id)

    def tick(self) -> bool:
        """Decrement remaining turns and remove when expired."""
        if self.turns <= 0:
            return True  # Permanent effect

        self.turns -= 1
        if self.turns <= 0:
            self.remove()
            return False
        return True


def create_stat_buff(
    stats: Stats,
    *,
    name: str = "buff",
    turns: int = 1,
    id: str | None = None,
    **modifiers: float,
) -> StatModifier:
    """Create and apply a :class:`StatModifier` to ``stats``.

    Keyword arguments ending with ``_mult`` are treated as multipliers for the
    corresponding stat; others are additive deltas. The new modifier is applied
    immediately and returned for tracking in an :class:`EffectManager`.
    """

    deltas: dict[str, float] = {}
    mults: dict[str, float] = {}
    for key, value in modifiers.items():
        if key.endswith("_mult"):
            mults[key[:-5]] = float(value)
        else:
            deltas[key] = float(value)
    effect = StatModifier(
        stats=stats,
        name=name,
        turns=turns,
        id=id or name,
        deltas=deltas or None,
        multipliers=mults or None,
    )
    effect.apply()
    return effect


@dataclass
class DamageOverTime:
    """Base class for damage over time effects."""

    name: str
    damage: int
    turns: int
    id: str
    source: Stats | None = None

    async def tick(self, target: Stats, *_: object) -> bool:
        attacker = self.source or target
        dtype = getattr(self, "damage_type", None)
        if dtype is None:
            dtype = getattr(attacker, "damage_type", target.damage_type)
        dmg = dtype.on_dot_damage_taken(
            self.damage,
            attacker,
            target,
        )
        dmg = dtype.on_party_dot_damage_taken(
            dmg,
            attacker,
            target,
        )
        source_type = getattr(attacker, "damage_type", None)
        if source_type is not dtype:
            dmg = source_type.on_party_dot_damage_taken(dmg, attacker, target)
        await target.apply_damage(int(dmg), attacker=attacker)
        self.turns -= 1
        return self.turns > 0


@dataclass
class HealingOverTime:
    """Base class for healing over time effects."""

    name: str
    healing: int
    turns: int
    id: str
    source: Stats | None = None

    async def tick(self, target: Stats, *_: object) -> bool:
        healer = self.source or target
        dtype = getattr(self, "damage_type", None)
        if dtype is None:
            dtype = getattr(healer, "damage_type", target.damage_type)
        heal = dtype.on_hot_heal_received(self.healing, healer, target)
        heal = dtype.on_party_hot_heal_received(heal, healer, target)
        source_type = getattr(healer, "damage_type", None)
        if source_type is not dtype:
            heal = source_type.on_party_hot_heal_received(heal, healer, target)
        await target.apply_healing(int(heal), healer=healer)
        self.turns -= 1
        return self.turns > 0


class EffectManager:
    """Manage DoT and HoT effects on a Stats object."""

    def __init__(self, stats: Stats) -> None:
        self.stats = stats
        self.dots: list[DamageOverTime] = []
        self.hots: list[HealingOverTime] = []
        self.mods: list[StatModifier] = []
        self._console = Console()
        for eff in getattr(stats, "_pending_mods", []):
            self.mods.append(eff)
            self.stats.mods.append(eff.id)
        if hasattr(stats, "_pending_mods"):
            delattr(stats, "_pending_mods")

    def add_dot(self, effect: DamageOverTime, max_stacks: int | None = None) -> None:
        """Attach a DoT instance to the tracked stats.

        DoTs with the same ``id`` stack independently, allowing multiple
        copies to tick each turn.  When ``max_stacks`` is provided, extra
        applications beyond that limit are ignored rather than refreshed.
        """

        if max_stacks is not None:
            current = len([d for d in self.dots if d.id == effect.id])
            if current >= max_stacks:
                return
        self.dots.append(effect)
        self.stats.dots.append(effect.id)

    def add_hot(self, effect: HealingOverTime) -> None:
        """Attach a HoT instance to the tracked stats.

        Healing effects simply accumulate; each copy heals separately every
        tick with no inherent stack cap.
        """

        self.hots.append(effect)
        self.stats.hots.append(effect.id)

    def add_modifier(self, effect: StatModifier) -> None:
        """Attach a stat modifier to the tracked stats."""

        self.mods.append(effect)
        self.stats.mods.append(effect.id)

    def maybe_inflict_dot(self, attacker: Stats, damage: int) -> None:
        dot = attacker.damage_type.create_dot(damage, attacker)
        if dot is None:
            return
        rate = max(attacker.effect_hit_rate - self.stats.effect_resistance, 0.0)
        chance = max(min(rate * random.uniform(0.9, 1.1), 1.0), 0.01)
        if random.random() < chance:
            self.add_dot(dot)

    async def tick(self, others: Optional["EffectManager"] = None) -> None:
        for collection, names in (
            (self.hots, self.stats.hots),
            (self.dots, self.stats.dots),
        ):
            expired: list[object] = []

            # Batch logging for performance when many effects are present
            if len(collection) > 10:
                effect_type = "HoT" if (collection and isinstance(collection[0], HealingOverTime)) else "DoT"
                color = "green" if effect_type == "HoT" else "light_red"
                self._console.log(f"[{color}]{self.stats.id} processing {len(collection)} {effect_type} effects[/]")

            # Process effects in parallel for better async performance when many are present
            if len(collection) > 20:
                # Parallel processing for large collections
                async def tick_effect(eff):
                    if len(collection) <= 10:
                        color = "green" if isinstance(eff, HealingOverTime) else "light_red"
                        self._console.log(f"[{color}]{self.stats.id} {eff.name} tick[/]")
                    return await eff.tick(self.stats), eff

                # Process in batches to avoid overwhelming the event loop
                batch_size = 50
                for i in range(0, len(collection), batch_size):
                    batch = collection[i:i + batch_size]
                    results = await asyncio.gather(*[tick_effect(eff) for eff in batch])
                    for still_active, eff in results:
                        if not still_active:
                            expired.append(eff)
                    # Early termination: if target dies, stop processing remaining effects
                    if self.stats.hp <= 0:
                        break
            else:
                # Sequential processing for smaller collections
                for eff in collection:
                    # Only log individual effects if there are few of them
                    if len(collection) <= 10:
                        color = "green" if isinstance(eff, HealingOverTime) else "light_red"
                        self._console.log(f"[{color}]{self.stats.id} {eff.name} tick[/]")
                    if not await eff.tick(self.stats):
                        expired.append(eff)
                    # Early termination: if target dies, stop processing remaining effects
                    if self.stats.hp <= 0:
                        break

            for eff in expired:
                collection.remove(eff)
                if eff.id in names:
                    names.remove(eff.id)

        expired_mods: list[StatModifier] = []
        for mod in self.mods:
            self._console.log(f"[yellow]{self.stats.id} {mod.name} tick[/]")
            if not mod.tick():
                expired_mods.append(mod)
        for mod in expired_mods:
            self.mods.remove(mod)
            if mod.id in self.stats.mods:
                self.stats.mods.remove(mod.id)
        if self.stats.hp <= 0 and others is not None:
            for eff in list(self.dots):
                on_death = getattr(eff, "on_death", None)
                if callable(on_death):
                    on_death(others)

    async def on_action(self) -> bool:
        """Run any per-action hooks on attached effects.

        Returns ``False`` if any effect cancels the action.
        """

        for eff in list(self.dots) + list(self.hots):
            handler = getattr(eff, "on_action", None)
            if callable(handler):
                self._console.log(f"{self.stats.id} {eff.name} action")
                result = handler(self.stats)
                if hasattr(result, "__await"):
                    result = await result
                if result is False:
                    return False
        return True

    async def cleanup(self, target: Stats | None = None) -> None:
        """Clear remaining effects and detach status names from the stats.

        Battle resolution calls this to ensure we don't leak stacked effects
        into post-battle state snapshots.
        """
        # Remove references to effect instances
        self.dots.clear()
        self.hots.clear()
        self.mods.clear()
        # Clear status name lists on the stats object
        try:
            self.stats.dots = []
            self.stats.hots = []
            self.stats.mods = []
        except Exception:
            pass
