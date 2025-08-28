from dataclasses import dataclass
from dataclasses import field
import logging

from autofighter.character import CharacterType
from plugins.damage_types._base import DamageTypeBase
from plugins.damage_types.fire import Fire
from plugins.players._base import PlayerBase

log = logging.getLogger(__name__)


@dataclass
class Player(PlayerBase):
    id = "player"
    name = "Player"
    char_type = CharacterType.C
    damage_type: DamageTypeBase = field(default_factory=Fire)
    prompt: str = "Player prompt placeholder"
    about: str = "Player description placeholder"

    def __post_init__(self) -> None:
        # Apply customization to base stats during instantiation
        self._apply_base_customization()
        # Call parent post_init for other initialization
        super().__post_init__()

    def _apply_base_customization(self) -> None:
        """Apply player customization directly to base stats instead of using mods."""
        try:
            # Import here to avoid circular imports
            import json
            import os
            import sqlite3

            # Check if we have a database path set up
            db_path = os.getenv("AF_DB_PATH")
            db_key = os.getenv("AF_DB_KEY")

            if not db_path:
                # No database path, skip customization
                return

            # Try to connect to the database
            if db_key:
                # Use sqlcipher if key is provided
                try:
                    import sqlcipher3
                    conn = sqlcipher3.connect(db_path)
                    conn.execute(f"PRAGMA key = '{db_key}'")
                except ImportError:
                    # Fall back to regular sqlite
                    conn = sqlite3.connect(db_path)
            else:
                conn = sqlite3.connect(db_path)

            # Ensure options table exists
            conn.execute("CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)")

            # Load customization stats from options table
            cur = conn.execute("SELECT value FROM options WHERE key = ?", ("player_stats",))
            row = cur.fetchone()

            if row:
                stats = json.loads(row[0])

                # Apply customization directly to base stats
                hp_bonus = stats.get("hp", 0)
                attack_bonus = stats.get("attack", 0)
                defense_bonus = stats.get("defense", 0)

                if hp_bonus > 0:
                    multiplier = 1 + hp_bonus * 0.01
                    current_base_hp = self.get_base_stat("max_hp")
                    new_base_hp = int(current_base_hp * multiplier)
                    self.set_base_stat("max_hp", new_base_hp)

                if attack_bonus > 0:
                    multiplier = 1 + attack_bonus * 0.01
                    current_base_atk = self.get_base_stat("atk")
                    new_base_atk = int(current_base_atk * multiplier)
                    self.set_base_stat("atk", new_base_atk)

                if defense_bonus > 0:
                    multiplier = 1 + defense_bonus * 0.01
                    current_base_def = self.get_base_stat("defense")
                    new_base_def = int(current_base_def * multiplier)
                    self.set_base_stat("defense", new_base_def)

                # Update current HP to match new max HP
                self.hp = self.max_hp

                log.debug(
                    "Applied base customization: hp=%d, attack=%d, defense=%d -> final stats hp=%d, atk=%d, def=%d",
                    hp_bonus, attack_bonus, defense_bonus, self.max_hp, self.atk, self.defense
                )

            conn.close()

        except Exception as e:
            # If anything goes wrong, just continue without customization
            log.debug("Failed to apply customization: %s", e)
