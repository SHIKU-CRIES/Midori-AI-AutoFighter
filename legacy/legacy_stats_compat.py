"""
Legacy stats compatibility utilities.

This module provides utilities to help bridge the gap between legacy direct stat 
modification and the new base stats + effects system.
"""

import logging
from typing import TYPE_CHECKING, Dict, Any, Union

if TYPE_CHECKING:
    from autofighter.stats import StatEffect

log = logging.getLogger(__name__)


class LegacyStatTracker:
    """
    Tracks stat modifications for legacy players that don't use the new Stats system.
    
    This helps ensure that temporary effects don't permanently modify character stats
    by tracking what changes should be temporary vs permanent.
    """
    
    def __init__(self):
        self._base_stats: Dict[str, Union[int, float]] = {}
        self._active_effects: Dict[str, Dict[str, Union[int, float]]] = {}
        self._initialized = False
    
    def initialize_base_stats(self, player_obj) -> None:
        """Initialize base stats from a player object."""
        if self._initialized:
            return
            
        # Common legacy stat names and their mappings
        stat_mapping = {
            'MHP': 'max_hp',
            'HP': 'hp', 
            'Atk': 'atk',
            'Def': 'defense',
            'CritRate': 'crit_rate',
            'CritDamageMod': 'crit_damage',
            'DodgeOdds': 'dodge_odds',
            'Mitigation': 'mitigation',
            'Regain': 'regain',
            'Vitality': 'vitality',
            'EffectHitRate': 'effect_hit_rate',
            'EffectRES': 'effect_resistance'
        }
        
        for legacy_name, modern_name in stat_mapping.items():
            if hasattr(player_obj, legacy_name):
                value = getattr(player_obj, legacy_name)
                self._base_stats[modern_name] = value
        
        self._initialized = True
        log.debug(f"Initialized base stats: {self._base_stats}")
    
    def add_temporary_effect(self, effect_name: str, stat_modifiers: Dict[str, Union[int, float]]) -> None:
        """Add a temporary effect that modifies stats."""
        self._active_effects[effect_name] = stat_modifiers.copy()
        log.debug(f"Added temporary effect '{effect_name}': {stat_modifiers}")
    
    def remove_temporary_effect(self, effect_name: str) -> bool:
        """Remove a temporary effect. Returns True if effect was removed."""
        if effect_name in self._active_effects:
            del self._active_effects[effect_name]
            log.debug(f"Removed temporary effect '{effect_name}'")
            return True
        return False
    
    def calculate_runtime_stat(self, stat_name: str) -> Union[int, float]:
        """Calculate the runtime value for a stat (base + effects)."""
        base_value = self._base_stats.get(stat_name, 0)
        
        # Add all effect modifiers
        total_modifier = 0
        for effect_modifiers in self._active_effects.values():
            if stat_name in effect_modifiers:
                total_modifier += effect_modifiers[stat_name]
        
        return base_value + total_modifier
    
    def get_base_stat(self, stat_name: str) -> Union[int, float]:
        """Get the base value of a stat."""
        return self._base_stats.get(stat_name, 0)
    
    def set_base_stat(self, stat_name: str, value: Union[int, float]) -> None:
        """Set the base value of a stat (for permanent changes like leveling)."""
        self._base_stats[stat_name] = value
        log.debug(f"Set base stat '{stat_name}' to {value}")
    
    def apply_runtime_stats_to_player(self, player_obj) -> None:
        """Apply the calculated runtime stats back to the player object."""
        stat_mapping = {
            'max_hp': 'MHP',
            'hp': 'HP',
            'atk': 'Atk', 
            'defense': 'Def',
            'crit_rate': 'CritRate',
            'crit_damage': 'CritDamageMod',
            'dodge_odds': 'DodgeOdds',
            'mitigation': 'Mitigation',
            'regain': 'Regain',
            'vitality': 'Vitality',
            'effect_hit_rate': 'EffectHitRate',
            'effect_resistance': 'EffectRES'
        }
        
        for modern_name, legacy_name in stat_mapping.items():
            if hasattr(player_obj, legacy_name):
                runtime_value = self.calculate_runtime_stat(modern_name)
                setattr(player_obj, legacy_name, runtime_value)
    
    def restore_base_stats_to_player(self, player_obj) -> None:
        """Restore base stats to the player object (removing all effects)."""
        stat_mapping = {
            'max_hp': 'MHP',
            'hp': 'HP',
            'atk': 'Atk',
            'defense': 'Def', 
            'crit_rate': 'CritRate',
            'crit_damage': 'CritDamageMod',
            'dodge_odds': 'DodgeOdds',
            'mitigation': 'Mitigation',
            'regain': 'Regain',
            'vitality': 'Vitality',
            'effect_hit_rate': 'EffectHitRate',
            'effect_resistance': 'EffectRES'
        }
        
        for modern_name, legacy_name in stat_mapping.items():
            if hasattr(player_obj, legacy_name) and modern_name in self._base_stats:
                setattr(player_obj, legacy_name, self._base_stats[modern_name])
    
    def clear_all_effects(self) -> None:
        """Remove all active effects."""
        self._active_effects.clear()
        log.debug("Cleared all temporary effects")


# Global registry for legacy players
_legacy_trackers: Dict[str, LegacyStatTracker] = {}


def get_legacy_tracker(player_name: str) -> LegacyStatTracker:
    """Get or create a legacy stat tracker for a player."""
    if player_name not in _legacy_trackers:
        _legacy_trackers[player_name] = LegacyStatTracker()
    return _legacy_trackers[player_name]


def apply_temporary_stat_change(player_obj, effect_name: str, stat_changes: Dict[str, Union[int, float]]) -> None:
    """
    Apply a temporary stat change to a legacy player object.
    
    This should be used instead of directly modifying player stats for temporary effects.
    """
    if not hasattr(player_obj, 'PlayerName'):
        log.warning("Player object missing PlayerName, cannot track stats")
        return
    
    tracker = get_legacy_tracker(player_obj.PlayerName)
    tracker.initialize_base_stats(player_obj)
    tracker.add_temporary_effect(effect_name, stat_changes)
    tracker.apply_runtime_stats_to_player(player_obj)


def remove_temporary_stat_change(player_obj, effect_name: str) -> None:
    """Remove a temporary stat change from a legacy player object."""
    if not hasattr(player_obj, 'PlayerName'):
        log.warning("Player object missing PlayerName, cannot track stats")
        return
    
    tracker = get_legacy_tracker(player_obj.PlayerName)
    if tracker.remove_temporary_effect(effect_name):
        tracker.apply_runtime_stats_to_player(player_obj)


def make_permanent_stat_change(player_obj, stat_changes: Dict[str, Union[int, float]]) -> None:
    """
    Make a permanent change to base stats (for leveling, permanent upgrades).
    """
    if not hasattr(player_obj, 'PlayerName'):
        log.warning("Player object missing PlayerName, cannot track stats")
        return
    
    tracker = get_legacy_tracker(player_obj.PlayerName)
    tracker.initialize_base_stats(player_obj)
    
    # Update base stats
    for stat_name, change in stat_changes.items():
        current_base = tracker.get_base_stat(stat_name)
        tracker.set_base_stat(stat_name, current_base + change)
    
    # Apply to player object
    tracker.apply_runtime_stats_to_player(player_obj)


def restore_base_stats(player_obj) -> None:
    """Restore a player to their base stats (remove all temporary effects)."""
    if not hasattr(player_obj, 'PlayerName'):
        log.warning("Player object missing PlayerName, cannot track stats")
        return
    
    tracker = get_legacy_tracker(player_obj.PlayerName)
    tracker.clear_all_effects()
    tracker.restore_base_stats_to_player(player_obj)