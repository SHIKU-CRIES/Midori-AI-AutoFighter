from autofighter.effects import HealingOverTime
from plugins.damage_types.light import Light
from plugins.damage_types._base import DamageTypeBase


class RadiantRegeneration(HealingOverTime):
    plugin_type = "hot"
    # Include element in the id so frontends can infer visuals without extra metadata
    id = "light_radiant_regeneration"
    damage_type: DamageTypeBase = Light()

    def __init__(self, healing: int = 5, turns: int = 2) -> None:
        super().__init__("Radiant Regeneration", healing, turns, self.id)
