from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class MimicPlayerCopy:
    """Mimic's passive - copies player stats and passive at half strength."""
    plugin_type = "passive"
    id = "mimic_player_copy"
    name = "Player Copy"
    trigger = "battle_start"  # Triggers at start of battle to copy player
    max_stacks = 1  # Only one instance per character

    # Class-level tracking of copied stats and passives
    _copied_stats: ClassVar[dict[int, dict]] = {}  # entity_id -> copied_stats
    _copied_passive: ClassVar[dict[int, str]] = {}  # entity_id -> passive_id

    async def apply(self, target: "Stats") -> None:
        """Apply Mimic's player copying mechanics."""
        entity_id = id(target)

        # Initialize tracking if not present
        if entity_id not in self._copied_stats:
            # In full implementation, would find the actual player entity
            player_stats = self._find_player_stats()
            self._copy_player_stats(target, player_stats)

        # Apply 25% debuff to all copied stats
        copied_stats = self._copied_stats[entity_id]

        # Apply copied stats with 25% reduction
        for stat_name, original_value in copied_stats.items():
            debuffed_value = int(original_value * 0.75)  # 25% debuff

            copy_effect = StatEffect(
                name=f"{self.id}_copied_{stat_name}",
                stat_modifiers={stat_name: debuffed_value - getattr(target, stat_name)},
                duration=-1,  # Permanent
                source=self.id,
            )
            target.add_effect(copy_effect)

        # Apply copied passive at half strength if present
        if entity_id in self._copied_passive:
            await self._apply_copied_passive(target)

    def _find_player_stats(self) -> dict:
        """Find and return player stats (simplified)."""
        # In full implementation, would scan the battle participants for player entity
        # For now, return simulated player stats
        return {
            "max_hp": 100,
            "atk": 50,
            "defense": 25,
            "mitigation": 10,
        }

    def _copy_player_stats(self, target: "Stats", player_stats: dict) -> None:
        """Copy player stats to Mimic."""
        entity_id = id(target)
        self._copied_stats[entity_id] = player_stats.copy()

        # Also copy player's passive if they have one
        # Simplified - assume player has "player_level_up_bonus" passive
        player_passive = "player_level_up_bonus"
        if player_passive:
            self._copied_passive[entity_id] = player_passive

    async def _apply_copied_passive(self, target: "Stats") -> None:
        """Apply copied passive at half strength."""
        entity_id = id(target)
        passive_id = self._copied_passive[entity_id]

        # Create a weakened version of the player's passive
        # This would normally require dynamically loading and modifying the passive
        # For now, apply a generic half-strength effect

        if passive_id == "player_level_up_bonus":
            # Player normally gets 1.35x level up bonus, Mimic gets 1.175x (halfway to 1.0)
            level_bonus_effect = StatEffect(
                name=f"{self.id}_copied_level_bonus",
                stat_modifiers={"exp_multiplier": 0.175},  # Half of 0.35 bonus
                duration=-1,  # Permanent
                source=self.id,
            )
            target.add_effect(level_bonus_effect)

    async def on_battle_start(self, target: "Stats", battle_participants: list) -> None:
        """Copy player stats and passive when battle starts."""
        # Find the actual player in battle participants
        player_entity = None
        for participant in battle_participants:
            if hasattr(participant, 'id') and participant.id == "player":
                player_entity = participant
                break

        if player_entity:
            # Copy actual player stats
            entity_id = id(target)
            self._copied_stats[entity_id] = {
                "max_hp": player_entity.max_hp,
                "atk": player_entity.atk,
                "defense": player_entity.defense,
                "mitigation": getattr(player_entity, 'mitigation', 0),
            }

            # Copy player's passives
            if hasattr(player_entity, 'passives') and player_entity.passives:
                self._copied_passive[entity_id] = player_entity.passives[0]  # Copy first passive

    @classmethod
    def get_copied_stats(cls, target: "Stats") -> dict:
        """Get the stats copied from player."""
        return cls._copied_stats.get(id(target), {})

    @classmethod
    def get_copied_passive(cls, target: "Stats") -> str:
        """Get the passive copied from player."""
        return cls._copied_passive.get(id(target), None)
