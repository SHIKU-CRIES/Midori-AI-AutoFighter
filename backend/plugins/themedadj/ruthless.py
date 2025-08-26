from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Ruthless:
    plugin_type = "themedadj"
    id = "ruthless"
    name = "Ruthless"

    def apply(self, target) -> None:
        target.crit_damage = target.crit_damage * 1.15
