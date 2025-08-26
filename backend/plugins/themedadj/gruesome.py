from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Gruesome:
    plugin_type = "themedadj"
    id = "gruesome"
    name = "Gruesome"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.05)
        target.crit_damage = target.crit_damage * 1.05
