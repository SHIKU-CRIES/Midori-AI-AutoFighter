from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Poisonous:
    plugin_type = "themedadj"
    id = "poisonous"
    name = "Poisonous"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.07)
        target.max_hp = int(target.max_hp * 1.93)
