from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Venomous:
    plugin_type = "themedadj"
    id = "venomous"
    name = "Venomous"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.1)
        target.max_hp = int(target.max_hp * 1.9)
