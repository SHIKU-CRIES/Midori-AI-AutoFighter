from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Atrocious:
    plugin_type = "themedadj"
    id = "atrocious"
    name = "Atrocious"

    def apply(self, target) -> None:
        target.max_hp = int(target.max_hp * 1.9)
        target.atk = int(target.atk * 1.1)
