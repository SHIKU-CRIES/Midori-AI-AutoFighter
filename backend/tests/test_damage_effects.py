import pytest

from autofighter.stats import Stats
from plugins import damage_effects
from plugins.damage_types.fire import Fire
from plugins.damage_types.light import Light


@pytest.mark.asyncio
async def test_create_fire_dot_sets_source():
    attacker = Stats(damage_type=Fire())
    dot = damage_effects.create_dot("Fire", 100, attacker)
    assert dot is not None
    assert dot.source is attacker
    assert dot.id == "blazing_torment"


@pytest.mark.asyncio
async def test_create_light_hot_sets_source():
    healer = Stats(damage_type=Light())
    hot = damage_effects.create_hot("Light", healer)
    assert hot is not None
    assert hot.source is healer
    assert hot.id == "light_radiant_regeneration"
