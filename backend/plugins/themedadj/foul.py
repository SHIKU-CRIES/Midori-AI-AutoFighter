from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Foul:
    plugin_type = "themedadj"
    id = "foul"
    name = "Foul"

    def apply(self, target) -> None:
        target.defense = int(target.defense * 1.95)
        target.dodge_odds = target.dodge_odds * 1.95
