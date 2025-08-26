import pytest

from autofighter.stats import BUS
from autofighter.stats import Stats
from autofighter.effects import EffectManager
from plugins.damage_types.dark import Dark


@pytest.mark.asyncio
async def test_shadow_siphon_applies_temporary_stat_buff():
    dark = Dark()
    actor = Stats(atk=100, defense=100, damage_type=dark)
    ally = Stats()
    actor.id = "actor"
    ally.id = "ally"
    actor.effect_manager = EffectManager(actor)
    ally.effect_manager = EffectManager(ally)
    allies = [actor, ally]

    await dark.on_action(actor, allies, [])

    await ally.effect_manager.tick()

    assert actor.atk > 100
    assert actor.defense > 100
    assert actor.effect_manager.mods

    mod = actor.effect_manager.mods[0]
    mod.tick()
    actor.effect_manager.mods.remove(mod)

    assert actor.atk == 100
    assert actor.defense == 100
    assert not actor.effect_manager.mods


@pytest.mark.asyncio
async def test_shadow_siphon_clears_on_battle_end():
    dark = Dark()
    actor = Stats(damage_type=dark)
    ally = Stats()
    actor.id = "actor"
    ally.id = "ally"
    actor.effect_manager = EffectManager(actor)
    ally.effect_manager = EffectManager(ally)
    allies = [actor, ally]

    await dark.on_action(actor, allies, [])
    BUS.emit("battle_end", actor)

    for member in allies:
        assert "shadow_siphon" not in member.dots
        assert all(d.id != "shadow_siphon" for d in member.effect_manager.dots)
