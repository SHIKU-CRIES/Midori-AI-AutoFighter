from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Dishonorable:
    plugin_type = "themedadj"
    id = "dishonorable"
    name = "Dishonorable"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.05)
        target.defense = int(target.defense * 1.95)
