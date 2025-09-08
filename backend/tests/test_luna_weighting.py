from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from autofighter.mapgen import MapNode
from autofighter.party import Party
from autofighter.rooms import utils
from plugins.players import Player


def test_luna_weighted_selection() -> None:
    random.seed(0)
    party = Party(members=[Player()])
    counts: dict[str, int] = {}
    for _ in range(200):
        foe = utils._choose_foe(party)
        counts[foe.id] = counts.get(foe.id, 0) + 1
    luna_count = counts.get("luna", 0)
    assert luna_count > 0
    counts.pop("luna", None)
    assert all(luna_count > c for c in counts.values())


def test_luna_can_be_boss() -> None:
    random.seed(0)
    party = Party(members=[Player()])
    node = MapNode(room_id=0, room_type="boss", floor=1, index=1, loop=1, pressure=0)
    foe = utils._build_foes(node, party)[0]
    assert foe.id == "luna"
    assert foe.rank == "boss"
