from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Intimidating:
    plugin_type = "themedadj"
    id = "intimidating"
    name = "Intimidating"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.95)
        target.defense = int(target.defense * 1.05)
