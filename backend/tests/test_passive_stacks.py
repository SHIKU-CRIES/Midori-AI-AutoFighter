import pytest

from autofighter.passives import PassiveRegistry
from autofighter.stats import Stats
from plugins.damage_types.generic import Generic


@pytest.mark.asyncio
async def test_passive_stack_display():
    """Test that passives correctly report stack counts for the UI."""
    registry = PassiveRegistry()

    # Test Luna Lunar Reservoir - should show charge points
    luna = Stats(hp=1000, damage_type=Generic())
    luna.passives = ["luna_lunar_reservoir"]

    # Initially 0 charge
    description = registry.describe(luna)
    luna_passive = next((p for p in description if p["id"] == "luna_lunar_reservoir"), None)
    assert luna_passive is not None
    assert luna_passive["stacks"] == 0
    assert luna_passive["max_stacks"] == 200

    # After taking actions, should build charge
    for _ in range(10):  # 10 actions = 10 charge
        await registry.trigger("action_taken", luna)

    description = registry.describe(luna)
    luna_passive = next((p for p in description if p["id"] == "luna_lunar_reservoir"), None)
    assert luna_passive["stacks"] == 10


@pytest.mark.asyncio
async def test_ally_overload_stack_display():
    """Test that Ally Overload correctly reports charge for the UI."""
    registry = PassiveRegistry()

    ally = Stats(hp=1000, damage_type=Generic())
    ally.passives = ["ally_overload"]

    # Initially 0 charge
    description = registry.describe(ally)
    overload_passive = next((p for p in description if p["id"] == "ally_overload"), None)
    assert overload_passive is not None
    assert overload_passive["stacks"] == 0
    assert overload_passive["max_stacks"] == 120

    # After taking actions, should build charge
    # Note: Each action adds 10 charge but also decays 5 charge per action if inactive
    # So 5 actions = (10 - 5) * 5 = 25 charge
    for _ in range(5):  # 5 actions = 25 charge net (10 per action - 5 decay)
        await registry.trigger("action_taken", ally)

    description = registry.describe(ally)
    overload_passive = next((p for p in description if p["id"] == "ally_overload"), None)
    assert overload_passive["stacks"] == 25


@pytest.mark.asyncio
async def test_graygray_counter_stack_display():
    """Test that Graygray Counter Maestro correctly reports counter stacks for the UI."""
    registry = PassiveRegistry()

    graygray = Stats(hp=1000, damage_type=Generic())
    graygray.passives = ["graygray_counter_maestro"]

    # Initially 0 stacks
    description = registry.describe(graygray)
    counter_passive = next((p for p in description if p["id"] == "graygray_counter_maestro"), None)
    assert counter_passive is not None
    assert counter_passive["stacks"] == 0
    assert counter_passive["max_stacks"] == 50

    # After taking damage (triggering counters), should build stacks
    for _ in range(3):  # 3 damage instances = 3 counter stacks
        await registry.trigger("damage_taken", graygray)

    description = registry.describe(graygray)
    counter_passive = next((p for p in description if p["id"] == "graygray_counter_maestro"), None)
    assert counter_passive["stacks"] == 3


@pytest.mark.asyncio
async def test_carly_guardian_stack_display():
    """Test that Carly Guardian's Aegis correctly reports mitigation stacks for the UI."""
    registry = PassiveRegistry()

    carly = Stats(hp=1000, damage_type=Generic())
    carly.passives = ["carly_guardians_aegis"]

    # Initially 0 stacks
    description = registry.describe(carly)
    aegis_passive = next((p for p in description if p["id"] == "carly_guardians_aegis"), None)
    assert aegis_passive is not None
    assert aegis_passive["stacks"] == 0
    assert aegis_passive["max_stacks"] == 50

    # Simulate taking damage (which should add mitigation stacks)
    from plugins.passives.carly_guardians_aegis import CarlyGuardiansAegis
    carly_passive = CarlyGuardiansAegis()

    # Manually call on_damage_taken to simulate being hit
    for _ in range(2):  # 2 hits = 4 mitigation stacks (2 per hit)
        await carly_passive.on_damage_taken(carly, None, 100)

    description = registry.describe(carly)
    aegis_passive = next((p for p in description if p["id"] == "carly_guardians_aegis"), None)
    assert aegis_passive["stacks"] == 4


@pytest.mark.asyncio
async def test_bubbles_burst_stack_display():
    """Test that Bubbles Bubble Burst correctly reports attack buff stacks for the UI."""
    registry = PassiveRegistry()

    bubbles = Stats(hp=1000, damage_type=Generic())
    bubbles.passives = ["bubbles_bubble_burst"]

    # Initially 0 stacks
    description = registry.describe(bubbles)
    burst_passive = next((p for p in description if p["id"] == "bubbles_bubble_burst"), None)
    assert burst_passive is not None
    assert burst_passive["stacks"] == 0
    assert burst_passive["max_stacks"] == 20

    # Simulate bubble bursts by manually adding attack buff effects
    from autofighter.stats import StatEffect

    # Add a couple of bubble burst attack buffs
    for i in range(3):
        attack_buff = StatEffect(
            name=f"bubbles_bubble_burst_burst_bonus_{i}",
            stat_modifiers={"atk": int(bubbles.atk * 0.1)},
            duration=-1,
            source="bubbles_bubble_burst",
        )
        bubbles.add_effect(attack_buff)

    description = registry.describe(bubbles)
    burst_passive = next((p for p in description if p["id"] == "bubbles_bubble_burst"), None)
    assert burst_passive["stacks"] == 3
