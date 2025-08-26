from dataclasses import dataclass

from . import stat_buff


@stat_buff
@dataclass
class Malicious:
    plugin_type = "themedadj"
    id = "malicious"
    name = "Malicious"

    def apply(self, target) -> None:
        target.atk = int(target.atk * 1.07)
