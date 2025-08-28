from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Eerie:
    plugin_type = "themedadj"
    id = "eerie"
    name = "Eerie"

    def apply(self, target) -> None:
        target.dodge_odds = target.dodge_odds * 1.05
