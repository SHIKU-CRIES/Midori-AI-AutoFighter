from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Predatory:
    plugin_type = "themedadj"
    id = "predatory"
    name = "Predatory"

    def apply(self, target) -> None:
        target.dodge_odds = target.dodge_odds * 1.1
        target.crit_rate = target.crit_rate + 0.05
