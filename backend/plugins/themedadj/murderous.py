from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Murderous:
    plugin_type = "themedadj"
    id = "murderous"
    name = "Murderous"

    def apply(self, target) -> None:
        target.crit_rate = target.crit_rate + 0.15
