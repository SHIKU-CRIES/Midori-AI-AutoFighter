from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Sinister:
    plugin_type = "themedadj"
    id = "sinister"
    name = "Sinister"

    def apply(self, target) -> None:
        target.dodge_odds = target.dodge_odds * 1.05
        target.crit_damage = target.crit_damage * 1.05
