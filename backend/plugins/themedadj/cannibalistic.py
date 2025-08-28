from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Cannibalistic:
    plugin_type = "themedadj"
    id = "cannibalistic"
    name = "Cannibalistic"

    def apply(self, target) -> None:
        target.max_hp = int(target.max_hp + (target.max_hp * 0.05))
