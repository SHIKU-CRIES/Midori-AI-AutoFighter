from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Depraved:
    plugin_type = "themedadj"
    id = "depraved"
    name = "Depraved"

    def apply(self, target) -> None:
        target.defense = int(target.defense - (target.defense * 0.1))
        target.atk = int(target.atk + (target.atk * 0.1))
