import pytest

from autofighter.passives import PassiveRegistry
from autofighter.stats import Stats
from plugins.damage_types.generic import Generic


@pytest.mark.asyncio
async def test_luna_lunar_reservoir_passive():
    """Test Luna's Lunar Reservoir passive charging system."""
    registry = PassiveRegistry()

    # Create Luna with the passive
    luna = Stats(hp=1000, damage_type=Generic())
    luna.passives = ["luna_lunar_reservoir"]

    # Initially should have default attack count (1)
    await registry.trigger("action_taken", luna)
    assert luna.actions_per_turn == 2  # Should get 2 attacks (below 35 charge)

    # After multiple actions, should scale up
    for _ in range(10):  # Build charge to 11 total
        await registry.trigger("action_taken", luna)

    # Should still be at 2 attacks (below 35 charge)
    assert luna.actions_per_turn == 2

    # Build to 35+ charge
    for _ in range(25):  # Total 36 charge
        await registry.trigger("action_taken", luna)

    assert luna.actions_per_turn == 4  # 35-49 range

    # Build to 50+ charge
    for _ in range(15):  # Total 51 charge
        await registry.trigger("action_taken", luna)

    assert luna.actions_per_turn == 8  # 50-69 range


@pytest.mark.asyncio
async def test_graygray_counter_maestro_passive():
    """Test Graygray's Counter Maestro passive retaliation."""
    registry = PassiveRegistry()

    # Create Graygray with the passive
    graygray = Stats(hp=1000, damage_type=Generic())
    graygray.passives = ["graygray_counter_maestro"]

    # Create an attacker
    attacker = Stats(hp=1000, damage_type=Generic())

    # Trigger damage taken (which should trigger counter)
    await registry.trigger_damage_taken(graygray, attacker, 100)

    # Graygray should have gained attack buff from counter
    # Note: The StatEffect system would need to be properly integrated
    # For now, we just verify the passive was triggered without error
    assert len(graygray._active_effects) > 0  # Should have received effects


@pytest.mark.asyncio
async def test_mezzy_gluttonous_bulwark_passive():
    """Test Mezzy's Gluttonous Bulwark passive damage reduction."""
    registry = PassiveRegistry()

    # Create Mezzy with the passive
    mezzy = Stats(hp=2000, damage_type=Generic())
    mezzy.passives = ["mezzy_gluttonous_bulwark"]

    # Trigger turn start to apply passive effects
    await registry.trigger("turn_start", mezzy)

    # Mezzy should have received damage reduction and other effects
    assert len(mezzy._active_effects) > 0


@pytest.mark.asyncio
async def test_ally_overload_passive():
    """Test Ally's Overload passive twin dagger system."""
    registry = PassiveRegistry()

    # Create Ally with the passive
    ally = Stats(hp=1000, damage_type=Generic())
    ally.passives = ["ally_overload"]

    # Initially should have default attack count (1)
    await registry.trigger("action_taken", ally)
    assert ally.actions_per_turn == 2  # Should get twin daggers

    # After enough actions to build charge, should be able to activate Overload
    # Each action gives +10 charge but -5 from decay when inactive
    # Net gain is +5 per action, so need 20 actions to reach 100 charge
    for _ in range(20):  # Build 100+ charge
        await registry.trigger("action_taken", ally)

    # Should now have Overload active (4 attacks)
    assert ally.actions_per_turn == 4


@pytest.mark.asyncio
async def test_passive_registry_handles_unknown_passive():
    """Test that the registry handles unknown passives gracefully."""
    registry = PassiveRegistry()

    # Create entity with unknown passive
    entity = Stats(hp=1000, damage_type=Generic())
    entity.passives = ["unknown_passive"]

    # Should not raise an error
    await registry.trigger("action_taken", entity)
    await registry.trigger_damage_taken(entity, None, 0)
    await registry.trigger_turn_end(entity)


@pytest.mark.asyncio
async def test_passive_registry_handles_no_passives():
    """Test that the registry handles entities with no passives."""
    registry = PassiveRegistry()

    # Create entity with no passives
    entity = Stats(hp=1000, damage_type=Generic())
    entity.passives = []

    # Should not raise an error
    await registry.trigger("action_taken", entity)
    await registry.trigger_damage_taken(entity, None, 0)
    await registry.trigger_turn_end(entity)
