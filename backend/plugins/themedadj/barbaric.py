from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Barbaric:
    plugin_type = "themedadj"
    id = "barbaric"
    name = "Barbaric"

    def apply(self, target) -> None:
        target.max_hp = int(target.max_hp * 1.1)
        target.defense = int(target.defense * 1.9)
