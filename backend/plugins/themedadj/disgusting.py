from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Disgusting:
    plugin_type = "themedadj"
    id = "disgusting"
    name = "Disgusting"

    def apply(self, target) -> None:
        target.defense = int(target.defense * 1.9)
