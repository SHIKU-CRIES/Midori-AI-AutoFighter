from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Perverted:
    plugin_type = "themedadj"
    id = "perverted"
    name = "Perverted"

    def apply(self, target) -> None:
        target.defense = int(target.defense * 1.9)
        target.dodge_odds = target.dodge_odds * 1.1
