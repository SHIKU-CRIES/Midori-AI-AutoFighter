"""
Unified summons system for the Midori AI AutoFighter game.

Provides a consistent framework for creating and managing summons across
characters, passives, cards, and relics.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import random
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional

from autofighter.stats import BUS
from autofighter.stats import Stats
from plugins.damage_types import get_damage_type
from plugins.damage_types import random_damage_type
from plugins.damage_types._base import DamageTypeBase

if TYPE_CHECKING:
    from autofighter.party import Party

log = logging.getLogger(__name__)


@dataclass
class Summon(Stats):
    """Represents a summoned entity with proper stat inheritance."""

    # Summon-specific properties
    summoner_id: str = ""
    summon_type: str = "generic"
    summon_source: str = "unknown"  # card/passive/relic that created this
    is_temporary: bool = True
    turns_remaining: int = -1  # -1 for permanent, >0 for temporary

    def __post_init__(self):
        """Initialize summon with proper inheritance from summoner."""
        super().__post_init__()
        # Mark this as a summon for identification
        if not hasattr(self, 'id') or not self.id:
            self.id = f"{self.summoner_id}_{self.summon_type}_summon"

    @classmethod
    def create_from_summoner(
        cls,
        summoner: Stats,
        summon_type: str = "generic",
        source: str = "unknown",
        stat_multiplier: float = 0.5,
        turns_remaining: int = -1,
        override_damage_type: Optional[DamageTypeBase] = None,
    ) -> "Summon":
        """Create a summon based on a summoner's stats.

        Args:
            summoner: The entity summoning this
            summon_type: Type identifier for the summon
            source: Source that created this summon (card/passive/relic name)
            stat_multiplier: Multiplier for inherited stats (default 0.5 = 50%)
            turns_remaining: How many turns this summon lasts (-1 = permanent)
            override_damage_type: Specific damage type, or None for random
        """
        # Calculate base stats at specified multiplier
        base_hp = int(summoner.max_hp * stat_multiplier)
        base_atk = int(summoner.atk * stat_multiplier)
        base_def = int(summoner.defense * stat_multiplier)

        # Determine damage type - high chance to match summoner, otherwise random
        if override_damage_type:
            damage_type = override_damage_type
        else:
            # 70% chance to match summoner's element, 30% chance for random
            if random.random() < 0.7 and hasattr(summoner, 'damage_type'):
                try:
                    # Try to get the same damage type as summoner
                    summoner_element = getattr(summoner.damage_type, 'id', 'Generic')
                    damage_type = get_damage_type(summoner_element)
                except Exception:
                    # Fallback to random if summoner's type is problematic
                    damage_type = random_damage_type()
            else:
                damage_type = random_damage_type()

        # Create the summon instance
        summon = cls(
            hp=base_hp,
            # Inherit damage type
            damage_type=damage_type,
            # Summon-specific properties
            summoner_id=getattr(summoner, 'id', str(id(summoner))),
            summon_type=summon_type,
            summon_source=source,
            turns_remaining=turns_remaining,
        )

        # Set base stats after creation (since they're init=False)
        summon._base_max_hp = base_hp
        summon._base_atk = base_atk
        summon._base_defense = base_def
        # Inherit other relevant stats at same multiplier
        summon._base_crit_rate = summoner.crit_rate * stat_multiplier
        summon._base_crit_damage = summoner.crit_damage * stat_multiplier
        summon._base_effect_hit_rate = summoner.effect_hit_rate * stat_multiplier
        summon._base_effect_resistance = summoner.effect_resistance * stat_multiplier
        summon._base_mitigation = summoner.mitigation * stat_multiplier
        summon._base_vitality = summoner.vitality * stat_multiplier

        # Copy summoner's passives at reduced effectiveness if applicable
        if hasattr(summoner, 'passives') and summoner.passives:
            # Only copy certain "safe" passives that make sense for summons
            safe_passives = ['critical_boost', 'elemental_affinity']  # Add more as needed
            summon.passives = [p for p in summoner.passives if any(sp in p for sp in safe_passives)]

        log.debug(f"Created {summon_type} summon for {summoner.id} with {stat_multiplier*100}% stats")

        return summon

    def tick_turn(self) -> bool:
        """Process a turn for this summon. Returns False if summon should be removed."""
        if self.turns_remaining > 0:
            self.turns_remaining -= 1
            if self.turns_remaining <= 0:
                log.debug(f"Summon {self.id} expired")
                return False
        return True

    def is_expired(self) -> bool:
        """Check if this summon has expired."""
        return self.turns_remaining == 0


class SummonManager:
    """Manages summons for the entire game."""

    # Class-level tracking of all active summons
    _active_summons: ClassVar[Dict[str, List[Summon]]] = {}
    _summon_limits: ClassVar[Dict[str, int]] = {}  # summoner_id -> max_summons
    _initialized: ClassVar[bool] = False

    @classmethod
    def initialize(cls):
        """Initialize the summon manager and event handlers."""
        if cls._initialized:
            return

        # Subscribe to battle events
        BUS.subscribe("battle_start", cls._on_battle_start)
        BUS.subscribe("battle_end", cls._on_battle_end)
        BUS.subscribe("turn_start", cls._on_turn_start)
        BUS.subscribe("turn_end", cls._on_turn_end)
        BUS.subscribe("entity_defeat", cls._on_entity_defeat)

        cls._initialized = True
        log.debug("SummonManager initialized")

    @classmethod
    def create_summon(
        cls,
        summoner: Stats,
        summon_type: str = "generic",
        source: str = "unknown",
        stat_multiplier: float = 0.5,
        turns_remaining: int = -1,
        override_damage_type: Optional[DamageTypeBase] = None,
        max_summons: int = 1,
    ) -> Optional[Summon]:
        """Create a new summon and add it to tracking.

        Args:
            summoner: The entity creating the summon
            summon_type: Type identifier for the summon
            source: Source creating this summon
            stat_multiplier: Stat inheritance multiplier
            turns_remaining: Duration (-1 = permanent)
            override_damage_type: Specific damage type
            max_summons: Maximum summons this summoner can have

        Returns:
            The created summon, or None if limit exceeded
        """
        cls.initialize()

        summoner_id = getattr(summoner, 'id', str(id(summoner)))

        # Initialize tracking for this summoner if needed
        if summoner_id not in cls._active_summons:
            cls._active_summons[summoner_id] = []
            cls._summon_limits[summoner_id] = max_summons

        # Check summon limit
        if len(cls._active_summons[summoner_id]) >= max_summons:
            log.debug(f"Summon limit ({max_summons}) reached for {summoner_id}")
            return None

        # Create the summon
        summon = Summon.create_from_summoner(
            summoner, summon_type, source, stat_multiplier, turns_remaining, override_damage_type
        )

        # Add to tracking
        cls._active_summons[summoner_id].append(summon)

        # Emit creation event
        BUS.emit("summon_created", summoner, summon, source)

        log.info(f"Created {summon_type} summon for {summoner_id} from {source}")
        return summon

    @classmethod
    def get_summons(cls, summoner_id: str) -> List[Summon]:
        """Get all active summons for a summoner."""
        return cls._active_summons.get(summoner_id, []).copy()

    @classmethod
    def remove_summon(cls, summon: Summon, reason: str = "unknown") -> bool:
        """Remove a summon from tracking."""
        summoner_id = summon.summoner_id
        if summoner_id in cls._active_summons:
            if summon in cls._active_summons[summoner_id]:
                cls._active_summons[summoner_id].remove(summon)
                BUS.emit("summon_removed", summon, reason)
                log.debug(f"Removed summon {summon.id} due to {reason}")
                return True
        return False

    @classmethod
    def remove_all_summons(cls, summoner_id: str, reason: str = "cleanup") -> int:
        """Remove all summons for a summoner."""
        count = 0
        if summoner_id in cls._active_summons:
            summons = cls._active_summons[summoner_id].copy()
            for summon in summons:
                if cls.remove_summon(summon, reason):
                    count += 1
        return count

    @classmethod
    def get_all_summons(cls) -> List[Summon]:
        """Get all active summons across all summoners."""
        all_summons = []
        for summons in cls._active_summons.values():
            all_summons.extend(summons)
        return all_summons

    @classmethod
    def _on_battle_start(cls, *args, **kwargs):
        """Handle battle start - reset temporary tracking."""
        log.debug("Battle started - summon tracking active")

    @classmethod
    def _on_battle_end(cls, *args, **kwargs):
        """Handle battle end - clean up temporary summons."""
        total_removed = 0
        for summoner_id in list(cls._active_summons.keys()):
            summons = cls._active_summons[summoner_id].copy()
            for summon in summons:
                if summon.is_temporary:
                    cls.remove_summon(summon, "battle_end")
                    total_removed += 1

        if total_removed > 0:
            log.debug(f"Cleaned up {total_removed} temporary summons at battle end")

    @classmethod
    def _on_turn_start(cls, entity, **kwargs):
        """Handle turn start - process summon turns."""
        entity_id = getattr(entity, 'id', str(id(entity)))
        if entity_id in cls._active_summons:
            summons = cls._active_summons[entity_id].copy()
            for summon in summons:
                if not summon.tick_turn():
                    cls.remove_summon(summon, "expired")

    @classmethod
    def _on_turn_end(cls, entity, **kwargs):
        """Handle turn end for summons."""
        # Could add turn-end processing here if needed
        pass

    @classmethod
    def _on_entity_defeat(cls, entity, **kwargs):
        """Handle entity defeat - remove their summons."""
        entity_id = getattr(entity, 'id', str(id(entity)))
        removed = cls.remove_all_summons(entity_id, "summoner_defeated")
        if removed > 0:
            log.debug(f"Removed {removed} summons due to summoner defeat")

    @classmethod
    def add_summons_to_party(cls, party: "Party") -> int:
        """Add all active summons to a party for battle. Returns number added."""
        added = 0
        all_summons = cls.get_all_summons()

        for summon in all_summons:
            # Check if summoner is in the party
            summoner_in_party = any(
                getattr(member, 'id', str(id(member))) == summon.summoner_id
                for member in party.members
            )

            if summoner_in_party and summon not in party.members:
                party.members.append(summon)
                added += 1

        if added > 0:
            log.debug(f"Added {added} summons to party for battle")

        return added

    @classmethod
    def cleanup(cls):
        """Clean up all summons and reset manager."""
        cls._active_summons.clear()
        cls._summon_limits.clear()
        log.debug("SummonManager cleaned up")


# Initialize the manager when module is imported
SummonManager.initialize()
