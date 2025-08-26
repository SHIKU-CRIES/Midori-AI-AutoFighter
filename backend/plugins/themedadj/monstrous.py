from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Monstrous:
    plugin_type = "themedadj"
    id = "monstrous"
    name = "Monstrous"

    def apply(self, target) -> None:
        target.max_hp = int(target.max_hp * 1.1)
        target.atk = int(target.atk * 1.1)
