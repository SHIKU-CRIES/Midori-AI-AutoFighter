from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from autofighter.party import Party
from autofighter.rooms.utils import _choose_foe
from plugins.damage_types._base import DamageTypeBase
from plugins.players import Player


def test_choose_foe_instantiates_damage_type() -> None:
    random.seed(0)
    party = Party(members=[Player()])
    foe = _choose_foe(party)
    assert isinstance(foe.damage_type, DamageTypeBase)
