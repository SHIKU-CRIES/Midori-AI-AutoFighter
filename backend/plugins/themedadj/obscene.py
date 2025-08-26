from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Obscene:
    plugin_type = "themedadj"
    id = "obscene"
    name = "Obscene"

    def apply(self, target) -> None:
        target.defense = int(target.defense * 1.9)
        target.dodge_odds = target.dodge_odds * 1.9
