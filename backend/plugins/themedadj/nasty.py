from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Nasty:
    plugin_type = "themedadj"
    id = "nasty"
    name = "Nasty"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.05)
        target.defense = int(target.defense * 1.95)
        target.dodge_odds = target.dodge_odds * 1.95
