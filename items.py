import math
import random

item_mods = ["Powerful", "Strong", "Enhanced", "Fortified", "Empowered", "Reinforced", "Supercharged", "Boosted", "Overclocked"]
item_types = ["damage", "defense", "utility"]

class ItemType():
    def __init__(self):
        """Initialises an Item object."""
        self.type = [random.choice(item_types)]
        self.power = round(random.uniform(1.001, 1.2), 2)
        self.name = f"{random.choice(item_mods).lower().title()} Blessing of {self.type[0].title()}"

    def upgrade(self, mod_fixed):
        """Upgrades the item's power stat."""
        self.power += max(math.log10(random.uniform(0.001, 0.01)) * math.log10(self.check_mods(mod_fixed)), 0.00001)
    
    def check_mods(self, temp_power: float):
        for index, item_mod in enumerate(item_mods):
            if item_mod.lower() in self.name.lower():
                return temp_power * ((index * 0.0005) + 1)
        
        return temp_power

    def on_damage_taken(self, pre_damage_taken: float):
        """This function is called when the player takes damage.
        If the item type is "defense", this function will handle the damage-related functionality."""
        total_output = 0

        if "defense" in str(self.name).lower():
            total_output = float(pre_damage_taken / self.power)
        else:
            total_output = float(pre_damage_taken)

        return total_output

    def on_damage_dealt(self, damage_delt: float):
        """This function is called when the player deals damage.
        If the item type is "damage", this function will handle the damage-related functionality."""
        total_output = 0
        
        if "damage" in str(self.name).lower():
            total_output = float(damage_delt * self.power)
        else:
            total_output = float(damage_delt)

        return total_output

    def stat_gain(self, desired_increase: float):
        """This function is called when the player gains stats.
        If the item type is "utility", this function will handle the dodge-related functionality."""
        total_output = 0

        if "utility" in str(self.name).lower():
            total_output = float(desired_increase * self.power)
        else:
            total_output = float(desired_increase)

        return total_output