from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Premeditated:
    plugin_type = "themedadj"
    id = "premeditated"
    name = "Premeditated"

    def apply(self, target) -> None:
        target.crit_rate = target.crit_rate + 0.1
