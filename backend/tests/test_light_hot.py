import pytest

from autofighter.effects import EffectManager
from autofighter.stats import Stats
from plugins.damage_types.light import Light


@pytest.mark.asyncio
async def test_radiant_regeneration_stacks():
    light = Light()
    actor = Stats(damage_type=light)
    ally = Stats()
    actor.effect_manager = EffectManager(actor)
    ally.effect_manager = EffectManager(ally)
    await light.on_action(actor, [actor, ally], [])
    await light.on_action(actor, [actor, ally], [])
    stacks = [h for h in ally.effect_manager.hots if h.id == "light_radiant_regeneration"]
    assert len(stacks) == 2


@pytest.mark.asyncio
async def test_light_heals_low_hp_ally():
    light = Light()
    actor = Stats(damage_type=light)
    actor.set_base_stat('atk', 50)
    ally = Stats(hp=20)
    ally.set_base_stat('max_hp', 100)
    actor.effect_manager = EffectManager(actor)
    ally.effect_manager = EffectManager(ally)
    proceed = await light.on_action(actor, [actor, ally], [])
    assert ally.hp > 20
    assert not proceed
