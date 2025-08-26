from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Callous:
    plugin_type = "themedadj"
    id = "callous"
    name = "Callous"

    def apply(self, target) -> None:
        target.defense = int(target.defense * 1.1)
        target.dodge_odds = target.dodge_odds * 1.9
