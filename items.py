import math
import random

class ItemType():
    def __init__(self):
        """Initialises an Item object."""
        item_mods = ["Powerful", "Strong", "Enhanced", "Fortified", "Empowered", "Reinforced", "Supercharged", "Boosted", "Overclocked"]
        item_types = ["damage", "defense", "utility"]
        self.type = [random.choice(item_types)]
        self.power = round(random.uniform(1.001, 1.2), 2)
        self.name = f"{random.choice(item_mods).lower().title()} Blessing of {self.type[0].title()}"

    def upgrade(self, mod_fixed):
        """Upgrades the item's power stat."""
        self.power += round(max(math.log10(random.uniform(0.001, 0.01) * mod_fixed), 0.0001), 2)

    def on_damage_taken(self, pre_damage_taken: float):
        """This function is called when the player takes damage.
        If the item type is "defense", this function will handle the damage-related functionality."""
        if "defense" in str(self.name).lower():
            return float(pre_damage_taken / self.power)
        else:
            return float(pre_damage_taken)

    def on_damage_dealt(self, damage_delt: float):
        """This function is called when the player deals damage.
        If the item type is "damage", this function will handle the damage-related functionality."""
        if "damage" in str(self.name).lower():
            return float(damage_delt * self.power)
        else:
            return float(damage_delt)

    def stat_gain(self, desired_increase: float):
        """This function is called when the player gains stats.
        If the item type is "utility", this function will handle the dodge-related functionality."""
        if "utility" in str(self.name).lower():
            return float(desired_increase * self.power)
        else:
            return float(desired_increase)