"""
Tests for the unified summons system.
"""

from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
import llms.torch_checker as torch_checker

from autofighter.party import Party
from autofighter.stats import BUS
from autofighter.summons import Summon
from autofighter.summons import SummonManager
from plugins.cards.phantom_ally import PhantomAlly
from plugins.damage_types.lightning import Lightning
from plugins.foes._base import FoeBase
from plugins.passives.becca_menagerie_bond import BeccaMenagerieBond
from plugins.players.ally import Ally
from plugins.players.becca import Becca


@pytest.mark.asyncio
async def test_summon_creation_basic(monkeypatch):
    """Test basic summon creation with stat inheritance."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    # Create summoner
    summoner = Ally()
    summoner.id = "test_summoner"
    # Set base stats directly
    summoner._base_atk = 100
    summoner._base_max_hp = 200
    summoner._base_defense = 50

    # Create summon
    summon = Summon.create_from_summoner(
        summoner=summoner,
        summon_type="test",
        source="test_source",
        stat_multiplier=0.5
    )

    # Verify stat inheritance
    assert summon.atk == 50  # 50% of 100
    assert summon.max_hp == 100  # 50% of 200
    assert summon.defense == 25  # 50% of 50
    assert summon.summoner_id == "test_summoner"
    assert summon.summon_type == "test"
    assert summon.summon_source == "test_source"
    assert summon.id == "test_summoner_test_summon"


@pytest.mark.asyncio
async def test_summon_manager_creation_and_tracking(monkeypatch):
    """Test SummonManager summon creation and tracking."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    # Clean up any existing state
    SummonManager.cleanup()

    summoner = Ally()
    summoner.id = "test_summoner"

    # Create summon via manager
    summon = SummonManager.create_summon(
        summoner=summoner,
        summon_type="test",
        source="test_source"
    )

    assert summon is not None
    assert summon.summoner_id == "test_summoner"

    # Verify tracking
    tracked_summons = SummonManager.get_summons("test_summoner")
    assert len(tracked_summons) == 1
    assert tracked_summons[0].id == summon.id


@pytest.mark.asyncio
async def test_summon_manager_limits(monkeypatch):
    """Test summon limits are enforced."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    summoner = Ally()
    summoner.id = "test_summoner"

    # Create first summon (should succeed)
    summon1 = SummonManager.create_summon(
        summoner=summoner,
        summon_type="test1",
        source="test_source",
        max_summons=1
    )
    assert summon1 is not None

    # Try to create second summon (should fail due to limit)
    summon2 = SummonManager.create_summon(
        summoner=summoner,
        summon_type="test2",
        source="test_source",
        max_summons=1
    )
    assert summon2 is None

    # Should still only have one summon
    tracked_summons = SummonManager.get_summons("test_summoner")
    assert len(tracked_summons) == 1


@pytest.mark.asyncio
async def test_summon_battle_lifecycle(monkeypatch):
    """Test summon cleanup during battle events."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    summoner = Ally()
    summoner.id = "test_summoner"

    # Create temporary summon
    summon = SummonManager.create_summon(
        summoner=summoner,
        summon_type="temporary",
        source="test_source",
        turns_remaining=1
    )
    assert summon is not None

    # Should be tracked
    assert len(SummonManager.get_summons("test_summoner")) == 1

    # Emit battle end - temporary summons should be cleaned up
    BUS.emit("battle_end", FoeBase())

    # Should be removed
    assert len(SummonManager.get_summons("test_summoner")) == 0


@pytest.mark.asyncio
async def test_summon_turn_expiration(monkeypatch):
    """Test summon expiration based on turn count."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    summoner = Ally()
    summoner.id = "test_summoner"

    # Create summon with 2 turn duration
    summon = SummonManager.create_summon(
        summoner=summoner,
        summon_type="timed",
        source="test_source",
        turns_remaining=2
    )

    assert len(SummonManager.get_summons("test_summoner")) == 1

    # First turn
    BUS.emit("turn_start", summoner)
    assert len(SummonManager.get_summons("test_summoner")) == 1
    assert summon.turns_remaining == 1

    # Second turn - should expire
    BUS.emit("turn_start", summoner)
    assert len(SummonManager.get_summons("test_summoner")) == 0


@pytest.mark.asyncio
async def test_phantom_ally_new_system(monkeypatch):
    """Test PhantomAlly card using new summons system."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    # Create party
    ally = Ally()
    ally.id = "ally"
    becca = Becca()
    becca.id = "becca"
    party = Party(members=[ally, becca])

    # Apply PhantomAlly card
    await PhantomAlly().apply(party)

    # Should have 3 members now (2 original + 1 phantom)
    assert len(party.members) == 3

    # One should be a phantom summon
    phantom = None
    for member in party.members:
        if hasattr(member, 'summon_type') and member.summon_type == "phantom":
            phantom = member
            break

    assert phantom is not None
    assert phantom.summon_source == "phantom_ally"
    assert phantom.turns_remaining == -1  # Should last the entire battle


@pytest.mark.asyncio
async def test_becca_jellyfish_summoning(monkeypatch):
    """Test Becca's jellyfish summoning using new system."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    # Create Becca
    becca = Becca()
    becca.id = "becca"
    becca.hp = 100
    becca._base_max_hp = 100

    # Create passive instance
    passive = BeccaMenagerieBond()

    # Test jellyfish summoning
    success = await passive.summon_jellyfish(becca, "electric")
    assert success is True

    # Should have paid HP cost
    assert becca.hp == 90  # 100 - 10% = 90

    # Should have created summon
    summons = SummonManager.get_summons("becca")
    assert len(summons) == 1

    jellyfish = summons[0]
    assert jellyfish.summon_type == "jellyfish_electric"
    assert jellyfish.summon_source == "becca_menagerie_bond"
    assert jellyfish.damage_type.__class__.__name__ == "Lightning"


@pytest.mark.asyncio
async def test_becca_summon_added_to_party(monkeypatch):
    """Summoning a jellyfish adds it to the party for battle."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    becca = Becca()
    becca.id = "becca"
    party = Party(members=[becca])

    passive = BeccaMenagerieBond()

    await passive.summon_jellyfish(becca, "electric", party)

    # Party should now include the summon
    assert len(party.members) == 2
    summon = next(m for m in party.members if m is not becca)
    assert summon.summon_source == "becca_menagerie_bond"


@pytest.mark.asyncio
async def test_collect_summons_grouped_by_owner(monkeypatch):
    """Ensure snapshot helper groups summons by summoner id."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    becca = Becca()
    becca.id = "becca"
    party = Party(members=[becca])
    passive = BeccaMenagerieBond()

    await passive.summon_jellyfish(becca, "electric", party)

    from services.room_service import _collect_summons

    grouped = _collect_summons(party.members)
    assert "becca" in grouped
    assert len(grouped["becca"]) == 1
    assert grouped["becca"][0]["owner_id"] == "becca"


@pytest.mark.asyncio
async def test_becca_jellyfish_replacement_creates_spirit(monkeypatch):
    """Test that replacing jellyfish creates spirit stacks."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    # Create Becca
    becca = Becca()
    becca.id = "becca"
    becca.hp = 100
    becca._base_max_hp = 100

    passive = BeccaMenagerieBond()

    # Summon first jellyfish
    await passive.summon_jellyfish(becca, "electric")
    assert passive.get_spirit_stacks(becca) == 0

    # Wait for cooldown
    passive._summon_cooldown[id(becca)] = 0
    becca.hp = 100  # Reset HP

    # Summon different jellyfish (should create spirit)
    await passive.summon_jellyfish(becca, "healing")
    assert passive.get_spirit_stacks(becca) == 1

    # Should still have one summon (replaced)
    summons = SummonManager.get_summons("becca")
    assert len(summons) == 1
    assert summons[0].summon_type == "jellyfish_healing"


@pytest.mark.asyncio
async def test_damage_type_inheritance(monkeypatch):
    """Test that summons inherit damage types correctly."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    # Create summoner with Lightning damage type
    summoner = Ally()
    summoner.id = "lightning_summoner"
    summoner.damage_type = Lightning()

    # Create multiple summons to test probability
    lightning_count = 0
    total_summons = 20

    for i in range(total_summons):
        summon = Summon.create_from_summoner(
            summoner=summoner,
            summon_type=f"test_{i}",
            source="test"
        )
        if summon.damage_type.__class__.__name__ == "Lightning":
            lightning_count += 1

    # Should have high percentage of Lightning damage types (around 70%)
    # Allow some variance due to randomness - at least 30% should be Lightning
    assert lightning_count >= 6  # At least 30% should be Lightning (lower bound due to randomness)


@pytest.mark.asyncio
async def test_summon_party_integration(monkeypatch):
    """Test that summons are properly added to parties for battle."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    # Create party
    ally = Ally()
    ally.id = "ally"
    party = Party(members=[ally])

    # Create summon
    summon = SummonManager.create_summon(
        summoner=ally,
        summon_type="test",
        source="test_source"
    )

    # Add summons to party
    added = SummonManager.add_summons_to_party(party)

    assert added == 1
    assert len(party.members) == 2
    assert summon in party.members


@pytest.mark.asyncio
async def test_summon_defeat_cleanup(monkeypatch):
    """Test that summons are cleaned up when summoner is defeated."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    SummonManager.cleanup()

    summoner = Ally()
    summoner.id = "test_summoner"

    # Create summon
    SummonManager.create_summon(
        summoner=summoner,
        summon_type="test",
        source="test_source"
    )

    assert len(SummonManager.get_summons("test_summoner")) == 1

    # Emit entity defeat for summoner
    BUS.emit("entity_defeat", summoner)

    # Summons should be cleaned up
    assert len(SummonManager.get_summons("test_summoner")) == 0


@pytest.mark.asyncio
async def test_summon_inheritance_with_effects(monkeypatch):
    """Test that summons inherit base stats, not runtime stats affected by temporary effects."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    # Create summoner with specific base stats
    summoner = Ally()
    summoner.id = "test_summoner"
    summoner._base_defense = 100
    summoner._base_mitigation = 2.0
    summoner._base_vitality = 1.5

    # Add a temporary effect that boosts stats
    from autofighter.stats import StatEffect
    boost_effect = StatEffect(
        name="test_boost",
        stat_modifiers={
            "defense": 50,       # +50 defense
            "mitigation": 1.0,   # +1.0 mitigation
            "vitality": 0.5      # +0.5 vitality
        },
        duration=5,
        source="test_card"
    )
    summoner.add_effect(boost_effect)

    # Verify effect is applied to runtime stats
    assert summoner.defense == 150  # 100 base + 50 effect
    assert summoner.mitigation == 3.0  # 2.0 base + 1.0 effect
    assert summoner.vitality == 2.0  # 1.5 base + 0.5 effect

    # Create summon with 50% stat inheritance
    summon = Summon.create_from_summoner(
        summoner=summoner,
        summon_type="test",
        source="test_source",
        stat_multiplier=0.5
    )

    # Summon should inherit from BASE stats only, ignoring temporary effects
    assert summon._base_defense == 50  # 50% of base 100 (ignores +50 effect)
    assert summon._base_mitigation == 1.0  # 50% of base 2.0 (ignores +1.0 effect)
    assert summon._base_vitality == 0.75  # 50% of base 1.5 (ignores +0.5 effect)

    # Runtime stats should include inherited beneficial effects
    # The summon inherits the beneficial StatEffect, which adds +25 defense, +0.5 mitigation, +0.25 vitality
    assert summon.defense == 75  # 50 base + 25 inherited effect (50% of +50)
    assert summon.mitigation == 1.5  # 1.0 base + 0.5 inherited effect (50% of +1.0)
    assert summon.vitality == 1.0  # 0.75 base + 0.25 inherited effect (50% of +0.5)


@pytest.mark.asyncio
async def test_summon_inherits_beneficial_effects(monkeypatch):
    """Test that summons inherit beneficial effects (buffs and HOTs) but not harmful effects (DOTs)."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    # Create summoner
    summoner = Ally()
    summoner.id = "test_summoner"
    summoner._base_defense = 100
    summoner._base_atk = 200

    # Add beneficial StatEffect (buff)
    from autofighter.stats import StatEffect
    buff_effect = StatEffect(
        name="test_buff",
        stat_modifiers={
            "atk": 50,       # +50 attack - beneficial
            "defense": 25,   # +25 defense - beneficial
        },
        duration=5,
        source="test_card"
    )
    summoner.add_effect(buff_effect)

    # Add EffectManager with HOT and StatModifier
    from autofighter.effects import EffectManager
    from autofighter.effects import HealingOverTime
    from autofighter.effects import StatModifier
    summoner.effect_manager = EffectManager(summoner)

    # Add HOT (beneficial)
    hot = HealingOverTime(
        name="test_hot",
        healing=100,
        turns=3,
        id="test_hot_id",
        source=summoner
    )
    summoner.effect_manager.add_hot(hot)

    # Add beneficial StatModifier
    stat_mod = StatModifier(
        stats=summoner,
        name="test_stat_buff",
        turns=4,
        id="test_stat_buff_id",
        deltas={"crit_rate": 0.1},  # +10% crit rate - beneficial
        multipliers={"crit_damage": 1.5}  # 1.5x crit damage - beneficial
    )
    summoner.effect_manager.add_modifier(stat_mod)

    # Create summon with 50% stat inheritance
    summon = Summon.create_from_summoner(
        summoner=summoner,
        summon_type="test",
        source="test_source",
        stat_multiplier=0.5
    )

    # Verify summon inherited beneficial StatEffect
    summon_effects = summon.get_active_effects()
    assert len(summon_effects) == 2  # One from StatEffect inheritance, one from StatModifier application

    # Find the inherited StatEffect (from summoner's StatEffect)
    stat_effect = next((e for e in summon_effects if e.name == "summon_test_buff"), None)
    assert stat_effect is not None
    assert stat_effect.stat_modifiers["atk"] == 25  # 50% of 50
    assert stat_effect.stat_modifiers["defense"] == 12.5  # 50% of 25
    assert stat_effect.duration == 5  # Same duration

    # Find the StatEffect created by the applied StatModifier
    modifier_effect = next((e for e in summon_effects if e.name == "summon_test_stat_buff_id"), None)
    assert modifier_effect is not None
    assert modifier_effect.stat_modifiers["crit_rate"] == 0.05  # 50% of 0.1
    assert modifier_effect.stat_modifiers["crit_damage"] == 0.25  # scaled multiplier bonus
    assert modifier_effect.duration == 4  # Same duration

    # Verify summon has effect manager
    assert hasattr(summon, 'effect_manager')
    assert summon.effect_manager is not None

    # Verify summon inherited HOT
    summon_hots = summon.effect_manager.hots
    assert len(summon_hots) == 1
    inherited_hot = summon_hots[0]
    assert inherited_hot.name == "summon_test_hot"
    assert inherited_hot.healing == 50  # 50% of 100
    assert inherited_hot.turns == 3  # Same duration

    # Verify summon inherited beneficial StatModifier
    summon_mods = summon.effect_manager.mods
    assert len(summon_mods) == 1
    inherited_mod = summon_mods[0]
    assert inherited_mod.name == "summon_test_stat_buff"
    assert inherited_mod.deltas["crit_rate"] == 0.05  # 50% of 0.1
    assert inherited_mod.multipliers["crit_damage"] == 1.25  # 1 + (0.5 * 0.5) bonus scaling
    assert inherited_mod.turns == 4  # Same duration


@pytest.mark.asyncio
async def test_summon_does_not_inherit_harmful_effects(monkeypatch):
    """Test that summons do NOT inherit harmful effects (DOTs, debuffs)."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    # Create summoner
    summoner = Ally()
    summoner.id = "test_summoner"

    # Add harmful StatEffect (debuff)
    from autofighter.stats import StatEffect
    debuff_effect = StatEffect(
        name="test_debuff",
        stat_modifiers={
            "atk": -50,      # -50 attack - harmful
            "defense": -25,  # -25 defense - harmful
        },
        duration=3,
        source="enemy_curse"
    )
    summoner.add_effect(debuff_effect)

    # Add EffectManager with DOT and harmful StatModifier
    from autofighter.effects import DamageOverTime
    from autofighter.effects import EffectManager
    from autofighter.effects import StatModifier
    summoner.effect_manager = EffectManager(summoner)

    # Add DOT (harmful)
    dot = DamageOverTime(
        name="test_dot",
        damage=50,
        turns=3,
        id="test_dot_id",
        source=summoner
    )
    summoner.effect_manager.add_dot(dot)

    # Add harmful StatModifier
    harmful_mod = StatModifier(
        stats=summoner,
        name="test_stat_debuff",
        turns=4,
        id="test_stat_debuff_id",
        deltas={"crit_rate": -0.1},  # -10% crit rate - harmful
        multipliers={"crit_damage": 0.5}  # 0.5x crit damage - harmful
    )
    summoner.effect_manager.add_modifier(harmful_mod)

    # Create summon
    summon = Summon.create_from_summoner(
        summoner=summoner,
        summon_type="test",
        source="test_source",
        stat_multiplier=0.5
    )

    # Verify summon did NOT inherit harmful StatEffect
    summon_effects = summon.get_active_effects()
    assert len(summon_effects) == 0  # No harmful effects should be inherited

    # Verify summon has effect manager but no harmful effects
    assert hasattr(summon, 'effect_manager')

    # Verify summon did NOT inherit DOT
    summon_dots = summon.effect_manager.dots
    assert len(summon_dots) == 0  # No DOTs should be inherited

    # Verify summon did NOT inherit harmful StatModifier
    summon_mods = summon.effect_manager.mods
    assert len(summon_mods) == 0  # No harmful modifiers should be inherited


@pytest.mark.asyncio
async def test_summon_inherits_mixed_effects_correctly(monkeypatch):
    """Test that summons inherit only beneficial parts when summoner has mixed effects."""
    monkeypatch.setattr(torch_checker, "is_torch_available", lambda: False)

    # Create summoner
    summoner = Ally()
    summoner.id = "test_summoner"

    # Add mixed StatEffect (some beneficial, some harmful modifiers)
    from autofighter.stats import StatEffect
    mixed_effect = StatEffect(
        name="mixed_effect",
        stat_modifiers={
            "atk": 100,      # +100 attack - beneficial
            "defense": -50,  # -50 defense - harmful
        },
        duration=3,
        source="complex_spell"
    )
    summoner.add_effect(mixed_effect)

    # Add another purely beneficial effect
    beneficial_effect = StatEffect(
        name="pure_buff",
        stat_modifiers={
            "crit_rate": 0.2,    # +20% crit rate - beneficial
            "vitality": 0.5,     # +0.5 vitality - beneficial
        },
        duration=5,
        source="blessing"
    )
    summoner.add_effect(beneficial_effect)

    # Set up effect manager
    from autofighter.effects import EffectManager
    summoner.effect_manager = EffectManager(summoner)

    # Create summon
    summon = Summon.create_from_summoner(
        summoner=summoner,
        summon_type="test",
        source="test_source",
        stat_multiplier=0.5
    )

    # Verify summon inherited only the purely beneficial effect
    # The mixed effect should be rejected because it has harmful modifiers
    summon_effects = summon.get_active_effects()
    assert len(summon_effects) == 1  # Only the pure buff should be inherited

    inherited_effect = summon_effects[0]
    assert inherited_effect.name == "summon_pure_buff"
    assert inherited_effect.stat_modifiers["crit_rate"] == 0.1  # 50% of 0.2
    assert inherited_effect.stat_modifiers["vitality"] == 0.25  # 50% of 0.5
