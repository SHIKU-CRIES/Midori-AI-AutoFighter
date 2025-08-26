from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Sociopathic:
    plugin_type = "themedadj"
    id = "sociopathic"
    name = "Sociopathic"

    def apply(self, target) -> None:
        target.dodge_odds = target.dodge_odds * 1.9
        target.atk = int(target.atk * 1.15)
