from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Belligerent:
    plugin_type = "themedadj"
    id = "belligerent"
    name = "Belligerent"

    def apply(self, target) -> None:
        target.dodge_odds = target.dodge_odds * 1.9
        target.atk = int(target.atk * 1.1)
