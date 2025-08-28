from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Ghastly:
    plugin_type = "themedadj"
    id = "ghastly"
    name = "Ghastly"

    def apply(self, target) -> None:
        target.max_hp = int(target.max_hp * 1.95)
        target.dodge_odds = target.dodge_odds * 1.05
