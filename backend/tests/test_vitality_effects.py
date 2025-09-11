import pytest

from autofighter.effects import DamageOverTime
from autofighter.stats import Stats


@pytest.mark.asyncio
async def test_healing_scales_with_vitality():
    healer = Stats()
    healer.set_base_stat('vitality', 2.0)
    target = Stats(hp=400)
    target.set_base_stat('max_hp', 1000)
    target.set_base_stat('vitality', 1.5)
    healed = await target.apply_healing(100, healer)
    expected = int(100 * healer.vitality * target.vitality)
    assert healed == expected
    assert target.hp == 400 + expected


@pytest.mark.asyncio
async def test_dot_scales_with_vitality():
    attacker = Stats()
    attacker.set_base_stat('vitality', 2.0)
    target_low = Stats()
    target_low.set_base_stat('defense', 1)
    target_low.set_base_stat('vitality', 1.0)
    target_high = Stats()
    target_high.set_base_stat('defense', 1)
    target_high.set_base_stat('vitality', 2.0)
    dot1 = DamageOverTime("bleed", 10, 1, "bleed", source=attacker)
    await dot1.tick(target_low)
    low_damage = target_low.last_damage_taken
    dot2 = DamageOverTime("bleed", 10, 1, "bleed", source=attacker)
    await dot2.tick(target_high)
    high_damage = target_high.last_damage_taken
    assert low_damage >= 1 and high_damage >= 1
    assert low_damage > high_damage
