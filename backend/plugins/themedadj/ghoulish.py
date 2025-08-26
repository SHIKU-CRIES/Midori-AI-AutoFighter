from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Ghoulish:
    plugin_type = "themedadj"
    id = "ghoulish"
    name = "Ghoulish"

    def apply(self, target) -> None:
        target.max_hp = int(target.max_hp * 1.95)
        target.atk = int(target.atk * 1.05)
