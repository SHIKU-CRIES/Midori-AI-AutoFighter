from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Odious:
    plugin_type = "themedadj"
    id = "odious"
    name = "Odious"

    def apply(self, target) -> None:
        target.defense = int(target.defense * 1.95)
