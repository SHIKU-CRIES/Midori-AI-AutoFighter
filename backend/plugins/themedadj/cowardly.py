from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Cowardly:
    plugin_type = "themedadj"
    id = "cowardly"
    name = "Cowardly"

    def apply(self, target) -> None:
        target.max_hp = int(target.max_hp * 1.2)
        target.atk = int(target.atk * 0.8)
