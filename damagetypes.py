
import random

player_damage_types = ["Wind", "Lightning", "Fire", "Ice", "Light", "Dark"]

class DamageType():
    def __init__(self, name):
        """Initialises the damage type of a player."""
        self.name = name