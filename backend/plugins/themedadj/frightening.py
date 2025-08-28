from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Frightening:
    plugin_type = "themedadj"
    id = "frightening"
    name = "Frightening"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.05)
        target.dodge_odds = target.dodge_odds * 1.95
