from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Execrable:
    plugin_type = "themedadj"
    id = "execrable"
    name = "Execrable"

    def apply(self, target) -> None:
        target.max_hp = int(target.max_hp * 1.9)
