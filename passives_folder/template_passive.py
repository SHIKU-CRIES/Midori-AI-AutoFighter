
class PassiveType:

    def __init__(self, name: str):
        self.name = name
        self.power: float = 1

    def activate(self, gamestate) -> None:
        """Applies the passive effect."""
        return gamestate

    def do_pre_turn(self):
        pass

    def heal_damage(self, input_healing: float):
        pass

    def take_damage(self, input_damage: float):
        pass

    def deal_damage(self, input_damage_mod: float):
        pass

    def damage_mitigation(self, damage_pre: float):
        pass

    def regain_hp(self):
        pass

    def damage_over_time(self):
        pass

    def heal_over_time(self):
        pass

    def crit_damage_mod(self, damage_pre: float):
        pass