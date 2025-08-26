from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Destructive:
    plugin_type = "themedadj"
    id = "destructive"
    name = "Destructive"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.1)
        target.crit_rate = target.crit_rate + 0.05
