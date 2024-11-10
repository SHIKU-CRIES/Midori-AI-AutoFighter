import random

class ItemType():
    def __init__(self):
        """Initialises an Item object."""
        item_types = ["damage", "defense", "utility"]
        self.type = [random.choice(item_types)]
        self.power = random.uniform(1.1, 1.9)
        self.name = "Blessing of " + self.type[0]

    def upgrade(self):
        """Upgrades the item to a random new type."""
        item_types = ["damage", "defense", "utility"]
        for current_type in self.type:
            item_types.remove(current_type)
        if len(item_types) == 0:
            raise Exception("Cannot upgrade item with all types")
        new_type = random.choice(item_types)
        self.type.append(new_type)

    def on_damage_taken(self, pre_damage_taken: float):
        """This function is called when the player takes damage.
        If the item type is "damage", this function will handle the damage-related functionality."""
        if self.type == "damage":
            return float(pre_damage_taken / self.power)
        else:
            return float(pre_damage_taken)

    def on_damage_dealt(self, damage_delt: float):
        """This function is called when the player deals damage.
        If the item type is "damage", this function will handle the damage-related functionality."""
        if self.type == "damage":
            return float(damage_delt * self.power)
        else:
            return float(damage_delt)

    def stat_gain(self, power: float):
        """This function is called when the player gains stats.
        If the item type is "utility", this function will handle the dodge-related functionality."""
        if self.type == "utility":
            return float(power * self.power)
        else:
            return float(power)