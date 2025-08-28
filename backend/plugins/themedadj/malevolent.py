from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Malevolent:
    plugin_type = "themedadj"
    id = "malevolent"
    name = "Malevolent"

    def apply(self, target) -> None:
        target.crit_damage = target.crit_damage * 1.05
        target.dodge_odds = target.dodge_odds * 1.95
