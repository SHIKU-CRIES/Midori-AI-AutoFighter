from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Cruel:
    plugin_type = "themedadj"
    id = "cruel"
    name = "Cruel"

    def apply(self, target) -> None:
        target.crit_damage = target.crit_damage * 1.05
