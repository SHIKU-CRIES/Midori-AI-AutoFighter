from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Dreadful:
    plugin_type = "themedadj"
    id = "dreadful"
    name = "Dreadful"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.05)
