from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Sadistic:
    plugin_type = "themedadj"
    id = "sadistic"
    name = "Sadistic"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.02)
        target.crit_damage = target.crit_damage * 1.08
