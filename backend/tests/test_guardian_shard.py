import asyncio

import pytest

from autofighter.cards import apply_cards
from autofighter.cards import award_card
from autofighter.party import Party
from autofighter.stats import BUS
from plugins.players._base import PlayerBase


def setup_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def test_guardian_shard_applies_bonus_after_no_deaths():
    loop = setup_event_loop()
    party = Party()
    ally1 = PlayerBase()
    ally2 = PlayerBase()
    party.members.extend([ally1, ally2])
    award_card(party, "guardian_shard")
    loop.run_until_complete(apply_cards(party))

    BUS.emit("battle_start", ally1)
    BUS.emit("battle_start", ally2)
    loop.run_until_complete(asyncio.sleep(0))
    BUS.emit("battle_end", ally1)
    loop.run_until_complete(asyncio.sleep(0))

    pre = ally1.mitigation
    BUS.emit("battle_start", ally1)
    BUS.emit("battle_start", ally2)
    loop.run_until_complete(asyncio.sleep(0))
    assert ally1.mitigation == pytest.approx(pre + 1)

    BUS.emit("battle_end", ally1)
    loop.run_until_complete(asyncio.sleep(0))
    assert ally1.mitigation == pytest.approx(pre)


def test_guardian_shard_no_bonus_after_death():
    loop = setup_event_loop()
    party = Party()
    ally1 = PlayerBase()
    ally2 = PlayerBase()
    party.members.extend([ally1, ally2])
    award_card(party, "guardian_shard")
    loop.run_until_complete(apply_cards(party))

    BUS.emit("battle_start", ally1)
    BUS.emit("battle_start", ally2)
    BUS.emit("death", ally1)
    loop.run_until_complete(asyncio.sleep(0))
    BUS.emit("battle_end", ally1)
    loop.run_until_complete(asyncio.sleep(0))

    pre = ally1.mitigation
    BUS.emit("battle_start", ally1)
    BUS.emit("battle_start", ally2)
    loop.run_until_complete(asyncio.sleep(0))
    assert ally1.mitigation == pytest.approx(pre)
