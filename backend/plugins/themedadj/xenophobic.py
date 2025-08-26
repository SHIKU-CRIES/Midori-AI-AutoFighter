from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Xenophobic:
    plugin_type = "themedadj"
    id = "xenophobic"
    name = "Xenophobic"

    def apply(self, target) -> None:
        target.defense = int(target.defense * 1.1)
