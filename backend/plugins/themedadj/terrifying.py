from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Terrifying:
    plugin_type = "themedadj"
    id = "terrifying"
    name = "Terrifying"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.9)
        target.defense = int(target.defense * 1.1)
