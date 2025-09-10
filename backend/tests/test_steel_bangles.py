import asyncio

import pytest

from autofighter.cards import apply_cards
from autofighter.cards import award_card
from autofighter.party import Party
from autofighter.stats import BUS
from autofighter.stats import Stats
import plugins.cards.steel_bangles as steel_bangles_module
import plugins.event_bus as event_bus_module


@pytest.mark.asyncio
async def test_steel_bangles_reduces_damage_once(monkeypatch) -> None:
    event_bus_module.bus._subs.clear()
    defender = Stats()
    attacker = Stats()
    party = Party([defender])
    award_card(party, "steel_bangles")
    await apply_cards(party)
    await asyncio.sleep(0)

    # Force damage reduction to trigger
    monkeypatch.setattr(steel_bangles_module.random, "random", lambda: 0.0)
    BUS.emit("damage_dealt", defender, attacker, 100, "attack", None, None, "attack")
    await asyncio.sleep(0.1)

    # Retrieve the original before_damage callback
    obj_ref, _wrapper = event_bus_module.bus._subs["before_damage"][0]
    callback = obj_ref() if callable(obj_ref) else obj_ref

    # First attack is reduced
    assert callback(defender, attacker, 100) == 97
    # Subsequent attacks are unaffected
    assert callback(defender, attacker, 100) == 100

