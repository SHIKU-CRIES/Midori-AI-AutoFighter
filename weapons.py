import random

class WeaponType:
    def __init__(self, name, damage, accuracy, critical_chance, game_str):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.critical_chance = critical_chance
        self.game_obj = game_str
        self.position = (0, 0)

    # Python terms
    game_bit = WeaponType("game_bit", 10, 0.8, 0.05, f"{random.getrandbits(1)}")

