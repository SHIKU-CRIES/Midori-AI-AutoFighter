
import random

class DamageType():
    def __init__(self, name :str, weakness :str, color):
        """Initialises the damage type of a player."""
        self.name = name
        self.weakness = weakness
        self.color = color
    
    def is_weak(self, type_check):
        if type_check == self.weakness:
            return True
        else:
            return False
    
    def is_resistance(self, type_check):
        if type_check == self.name:
            return True
        else:
            return False
    
    def damage_mod(self, incoming_damage, incoming_damge_type):
        if self.is_weak(incoming_damge_type):
            return incoming_damage * 5
        elif self.is_resistance(incoming_damge_type):
            return incoming_damage * 0.25
        else:
            return incoming_damage


Light = DamageType("light", "dark", (255, 255, 255))
Dark = DamageType("dark", "light", (102, 0, 102))

Wind = DamageType("wind", "lightning", (173, 216, 230))
Lightning = DamageType("lightning", "wind", (255, 255, 0))

Fire = DamageType("fire", "ice", (255, 0, 0))
Ice = DamageType("ice", "fire", (0, 255, 255))

all_damage_types = [Light, Dark, Wind, Lightning, Fire, Ice]

def random_damage_type():
    return random.choice(all_damage_types)

def get_damage_type(name):
    damage_type_list = []

    for damage_type in all_damage_types:
        if damage_type.name.lower() in name.lower():
            damage_type_list.append(damage_type)
    
    if len(damage_type_list) > 0:
        return random.choice(damage_type_list)
    
    return random_damage_type()