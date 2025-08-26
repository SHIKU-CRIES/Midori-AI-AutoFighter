from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Inhumane:
    plugin_type = "themedadj"
    id = "inhumane"
    name = "Inhumane"

    def apply(self, target) -> None:
        target.crit_damage = target.crit_damage * 1.1
