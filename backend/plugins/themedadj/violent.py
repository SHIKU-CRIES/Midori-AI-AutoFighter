from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Violent:
    plugin_type = "themedadj"
    id = "violent"
    name = "Violent"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.15)
        target.defense = int(target.defense * 0.85)
