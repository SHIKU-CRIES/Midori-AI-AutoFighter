from dataclasses import dataclass
from dataclasses import field

from plugins.players._base import PlayerBase


@dataclass
class RedirectPlayer(PlayerBase):
    stat_gain_map: dict[str, str] = field(
        default_factory=lambda: {"atk": "defense"}
    )


def test_adjust_redirects_attack_to_defense():
    p = RedirectPlayer()
    base_atk = p.atk
    base_def = p.defense
    p.adjust_stat_on_gain("atk", 5)
    assert p.atk == base_atk
    assert p.defense == base_def + 5
