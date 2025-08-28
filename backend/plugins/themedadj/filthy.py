from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Filthy:
    plugin_type = "themedadj"
    id = "filthy"
    name = "Filthy"

    def apply(self, target) -> None:
        target.defense = int(target.defense * 1.95)
