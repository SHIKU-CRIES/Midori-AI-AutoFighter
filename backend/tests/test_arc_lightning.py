import asyncio
from unittest.mock import patch

import pytest

from autofighter.party import Party
from autofighter.stats import BUS
from plugins.cards.arc_lightning import ArcLightning
import plugins.event_bus as event_bus_module
from plugins.foes._base import FoeBase
from plugins.players._base import PlayerBase


@pytest.mark.asyncio
async def test_arc_lightning_chains_damage() -> None:
    event_bus_module.bus._subs.clear()
    attacker = PlayerBase()
    foe1 = FoeBase()
    foe2 = FoeBase()
    party = Party([attacker])
    card = ArcLightning()
    await card.apply(party)
    BUS.emit("battle_start", foe1)
    BUS.emit("battle_start", foe2)
    BUS.emit("battle_start", attacker)
    initial = foe2.hp
    with patch("plugins.cards.arc_lightning.random.choice", return_value=foe2):
        BUS.emit("hit_landed", attacker, foe1, 100, "attack")
        await asyncio.sleep(0)
    assert foe2.hp < initial
