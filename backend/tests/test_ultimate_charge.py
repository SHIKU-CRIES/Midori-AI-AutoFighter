import pytest

from autofighter.party import Party
from autofighter.rooms.battle import BattleRoom
from autofighter.stats import BUS
from autofighter.stats import Stats
from plugins.damage_types.generic import Generic
from plugins.damage_types.ice import Ice
from plugins.players._base import PlayerBase


def test_charge_accumulates_and_caps():
    player = PlayerBase(damage_type=Generic())
    for _ in range(20):
        player.add_ultimate_charge()
    assert player.ultimate_charge == 15
    assert player.ultimate_ready is True


@pytest.mark.asyncio
async def test_ice_allies_gain_charge():
    actor = PlayerBase(damage_type=Generic())
    actor.id = "actor"
    ice = PlayerBase(damage_type=Ice())
    ice.id = "ice"
    foe = Stats()
    foe.id = "foe"
    foe.hp = 50
    room = BattleRoom()
    party = Party(members=[actor, ice])
    await room.resolve(party, {}, foe=foe)
    assert ice.ultimate_charge == actor.actions_per_turn


def test_use_ultimate_emits_event():
    player = PlayerBase(damage_type=Generic())
    player.ultimate_charge = 15
    player.ultimate_ready = True
    seen: list[Stats] = []

    def _handler(user):
        seen.append(user)

    BUS.subscribe("ultimate_used", _handler)
    try:
        assert player.use_ultimate() is True
        assert player.ultimate_charge == 0
        assert player.ultimate_ready is False
        assert seen == [player]
    finally:
        BUS.unsubscribe("ultimate_used", _handler)

