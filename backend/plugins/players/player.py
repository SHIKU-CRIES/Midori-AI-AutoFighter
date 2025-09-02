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
    passives: list[str] = field(default_factory=lambda: ["player_level_up_bonus"])

    def __post_init__(self) -> None:
        # Call parent post_init for other initialization
        # Note: Player customization is now handled centrally by _apply_player_customization()
        # in game.py to avoid conflicts and ensure consistency
        super().__post_init__()
