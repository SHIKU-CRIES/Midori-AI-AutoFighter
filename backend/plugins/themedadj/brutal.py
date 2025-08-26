from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Brutal:
    plugin_type = "themedadj"
    id = "brutal"
    name = "Brutal"

    def apply(self, target) -> None:
        target.crit_rate = target.crit_rate + 0.1
        target.dodge_odds = target.dodge_odds * 1.9
