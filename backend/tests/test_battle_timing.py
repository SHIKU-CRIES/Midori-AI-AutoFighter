import time

import pytest

from autofighter.mapgen import MapNode
from autofighter.party import Party
from autofighter.rooms.battle import BattleRoom
from autofighter.stats import Stats


@pytest.mark.asyncio
async def test_turn_pacing():
    node = MapNode(room_id=0, room_type="battle-normal", floor=1, index=1, loop=1, pressure=0)
    room = BattleRoom(node)
    player = Stats(hp=100, max_hp=100, atk=2000, defense=0)
    player.id = "p1"
    foe = Stats(hp=100, max_hp=100, atk=1, defense=0)
    foe.id = "f1"
    party = Party(members=[player])

    import autofighter.rooms.utils as rooms_module
    original = rooms_module._choose_foe
    rooms_module._choose_foe = lambda _party: foe
    start = time.perf_counter()
    await room.resolve(party, {})
    elapsed = time.perf_counter() - start
    rooms_module._choose_foe = original
    assert elapsed >= 0.5
