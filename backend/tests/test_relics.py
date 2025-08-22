import asyncio

import pytest

import plugins.event_bus as event_bus_module

from math import isclose
from autofighter.party import Party
from autofighter.stats import BUS
from autofighter.stats import Stats
from autofighter.relics import award_relic
from autofighter.relics import apply_relics
from plugins.players._base import PlayerBase
from plugins.effects.aftertaste import Aftertaste


def test_award_relics_stack():
    party = Party()
    member = PlayerBase()
    member.atk = 100
    party.members.append(member)
    assert award_relic(party, "bent_dagger") is not None
    assert award_relic(party, "bent_dagger") is not None
    apply_relics(party)
    assert party.relics == ["bent_dagger", "bent_dagger"]
    assert party.members[0].atk == int(100 * 1.03 * 1.03)


def test_bent_dagger_kill_trigger():
    event_bus_module.bus._subs.clear()
    party = Party()
    member = PlayerBase()
    enemy = PlayerBase()
    member.atk = 100
    enemy.hp = enemy.max_hp = 10
    party.members.append(member)
    award_relic(party, "bent_dagger")
    apply_relics(party)
    enemy.hp = 0
    BUS.emit("damage_taken", enemy, member, 10)
    assert member.atk == int(100 * 1.03 * 1.01)


def test_bent_dagger_kill_trigger_stacks():
    event_bus_module.bus._subs.clear()
    party = Party()
    member = PlayerBase()
    enemy = PlayerBase()
    member.atk = 100
    enemy.hp = enemy.max_hp = 10
    party.members.append(member)
    award_relic(party, "bent_dagger")
    award_relic(party, "bent_dagger")
    apply_relics(party)
    enemy.hp = 0
    BUS.emit("damage_taken", enemy, member, 10)
    expected = int(100 * 1.03 * 1.03 * 1.01 * 1.01)
    assert member.atk == expected


def test_lucky_button_stacks():
    party = Party()
    member = PlayerBase()
    member.crit_rate = 0.1
    party.members.append(member)
    award_relic(party, "lucky_button")
    award_relic(party, "lucky_button")
    apply_relics(party)
    assert isclose(party.members[0].crit_rate, 0.1 * 1.03 * 1.03)


def test_vengeful_pendant_reflects():
    event_bus_module.bus._subs.clear()
    party = Party()
    ally = PlayerBase()
    enemy = PlayerBase()
    ally.id = "ally"
    enemy.id = "enemy"
    ally.hp = 100
    enemy.hp = 100
    party.members.append(ally)
    award_relic(party, "vengeful_pendant")
    apply_relics(party)
    BUS.emit("damage_taken", ally, enemy, 20)
    assert enemy.hp == 100 - int(20 * 0.15)


def test_vengeful_pendant_stacks():
    event_bus_module.bus._subs.clear()
    party = Party()
    ally = PlayerBase()
    enemy = PlayerBase()
    ally.id = "ally"
    enemy.id = "enemy"
    ally.hp = 100
    enemy.hp = 100
    party.members.append(ally)
    award_relic(party, "vengeful_pendant")
    award_relic(party, "vengeful_pendant")
    apply_relics(party)
    BUS.emit("damage_taken", ally, enemy, 20)
    assert enemy.hp == 100 - int(20 * 0.15 * 2)


def test_guardian_charm_targets_lowest_hp():
    party = Party()
    low = PlayerBase()
    high = PlayerBase()
    low.hp = low.max_hp = 50
    high.hp = high.max_hp = 100
    party.members.extend([low, high])
    award_relic(party, "guardian_charm")
    apply_relics(party)
    assert low.defense == int(50 * 1.2)
    assert high.defense == 50


def test_herbal_charm_heals_each_turn():
    event_bus_module.bus._subs.clear()
    party = Party()
    member = PlayerBase()
    member.hp = 50
    member.max_hp = 100
    party.members.append(member)
    award_relic(party, "herbal_charm")
    apply_relics(party)
    BUS.emit("turn_start")
    assert member.hp == 50 + int(100 * 0.005)


def test_herbal_charm_stacks():
    event_bus_module.bus._subs.clear()
    party = Party()
    member = PlayerBase()
    member.hp = 50
    member.max_hp = 100
    party.members.append(member)
    award_relic(party, "herbal_charm")
    award_relic(party, "herbal_charm")
    apply_relics(party)
    BUS.emit("turn_start")
    assert member.hp == 50 + 2 * int(100 * 0.005)


def test_tattered_flag_buffs_survivors_on_death():
    event_bus_module.bus._subs.clear()
    party = Party()
    survivor = PlayerBase()
    victim = PlayerBase()
    survivor.atk = 100
    victim.hp = victim.max_hp = 10
    party.members.extend([survivor, victim])
    award_relic(party, "tattered_flag")
    apply_relics(party)
    victim.hp = 0
    BUS.emit("damage_taken", victim, survivor, 10)
    assert survivor.atk == int(100 * 1.03)


def test_tattered_flag_stacks():
    event_bus_module.bus._subs.clear()
    party = Party()
    survivor = PlayerBase()
    victim = PlayerBase()
    survivor.atk = 100
    victim.hp = victim.max_hp = 10
    party.members.extend([survivor, victim])
    award_relic(party, "tattered_flag")
    award_relic(party, "tattered_flag")
    apply_relics(party)
    victim.hp = 0
    BUS.emit("damage_taken", victim, survivor, 10)
    assert survivor.atk == int(100 * 1.03 * 1.03)


def test_shiny_pebble_first_hit_mitigation():
    event_bus_module.bus._subs.clear()
    party = Party()
    ally = PlayerBase()
    enemy = PlayerBase()
    party.members.append(ally)
    award_relic(party, "shiny_pebble")
    apply_relics(party)
    BUS.emit("damage_taken", ally, enemy, 10)
    assert isclose(ally.mitigation, 103)
    BUS.emit("turn_start")
    assert isclose(ally.mitigation, 100)


def test_shiny_pebble_stacks():
    event_bus_module.bus._subs.clear()
    party = Party()
    ally = PlayerBase()
    enemy = PlayerBase()
    party.members.append(ally)
    award_relic(party, "shiny_pebble")
    award_relic(party, "shiny_pebble")
    apply_relics(party)
    BUS.emit("damage_taken", ally, enemy, 10)
    assert isclose(ally.mitigation, 100 * 1.03 * 1.03)


def test_threadbare_cloak_shield_stacks():
    party = Party()
    a = PlayerBase()
    a.hp = a.max_hp = 100
    party.members.append(a)
    award_relic(party, "threadbare_cloak")
    award_relic(party, "threadbare_cloak")
    apply_relics(party)
    assert a.hp == 100 + int(100 * 0.03) * 2


def test_lucky_button_missed_crit():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    a.crit_rate = 0.1
    party.members.append(a)
    award_relic(party, "lucky_button")
    apply_relics(party)
    BUS.emit("crit_missed", a, None)
    BUS.emit("turn_start")
    assert isclose(a.crit_rate, 0.1 * 1.03 + 0.03, rel_tol=1e-4)
    BUS.emit("turn_end")
    assert isclose(a.crit_rate, 0.1 * 1.03, rel_tol=1e-4)


def test_old_coin_gold_and_discount():
    event_bus_module.bus._subs.clear()
    party = Party()
    award_relic(party, "old_coin")
    apply_relics(party)
    BUS.emit("gold_earned", 100)
    assert party.gold == int(100 * 0.03)
    BUS.emit("shop_purchase", 100)
    assert party.gold == int(100 * 0.03) + int(100 * 0.03)
    BUS.emit("shop_purchase", 100)
    assert party.gold == int(100 * 0.03) + int(100 * 0.03)


def test_wooden_idol_resist_buff():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    a.effect_resistance = 1.0
    party.members.append(a)
    award_relic(party, "wooden_idol")
    apply_relics(party)
    BUS.emit("debuff_resisted", a)
    BUS.emit("turn_start")
    assert isclose(a.effect_resistance, 1.03 + 0.01)
    BUS.emit("turn_end")
    assert isclose(a.effect_resistance, 1.03)


def test_pocket_manual_tenth_hit():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    b = PlayerBase()
    b.hp = 100
    party.members.append(a)
    award_relic(party, "pocket_manual")
    apply_relics(party)
    for i in range(9):
        BUS.emit("hit_landed", a, b, 10)
    assert b.hp == 100 - 0
    BUS.emit("hit_landed", a, b, 10)
    assert b.hp == 100 - int(10 * 0.03)


def test_arcane_flask_shields():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    a.hp = 50
    a.max_hp = 100
    party.members.append(a)
    award_relic(party, "arcane_flask")
    apply_relics(party)
    BUS.emit("ultimate_used", a)
    assert a.hp == 50 + int(100 * 0.2)


def test_echo_bell_repeats_first_action():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    b = PlayerBase()
    b.hp = 100
    party.members.append(a)
    award_relic(party, "echo_bell")
    apply_relics(party)
    BUS.emit("battle_start")
    b.hp -= 20
    BUS.emit("action_used", a, b, 20)
    assert b.hp == 100 - 20 - int(20 * 0.15)
    b.hp -= 20
    BUS.emit("action_used", a, b, 20)
    assert b.hp == 100 - 20 - int(20 * 0.15) - 20


@pytest.mark.asyncio
async def test_frost_sigil_applies_chill(monkeypatch):
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    b = PlayerBase()
    b.hp = b.max_hp = 100
    a.atk = 100
    party.members.append(a)
    award_relic(party, "frost_sigil")
    apply_relics(party)

    monkeypatch.setattr(Aftertaste, "rolls", lambda self: [self.base_pot] * self.hits)

    async def fake_apply_damage(self, amount, attacker=None):
        self.hp -= amount
        return amount

    monkeypatch.setattr(Stats, "apply_damage", fake_apply_damage, raising=False)

    BUS.emit("hit_landed", a, b, 10)
    await asyncio.sleep(0)

    assert b.hp == 100 - int(100 * 0.05)


@pytest.mark.asyncio
async def test_frost_sigil_stacks(monkeypatch):
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    b = PlayerBase()
    b.hp = b.max_hp = 100
    a.atk = 100
    party.members.append(a)
    award_relic(party, "frost_sigil")
    award_relic(party, "frost_sigil")
    apply_relics(party)

    monkeypatch.setattr(Aftertaste, "rolls", lambda self: [self.base_pot] * self.hits)

    async def fake_apply_damage(self, amount, attacker=None):
        self.hp -= amount
        return amount

    monkeypatch.setattr(Stats, "apply_damage", fake_apply_damage, raising=False)

    BUS.emit("hit_landed", a, b, 10)
    await asyncio.sleep(0)

    assert b.hp == 100 - int(100 * 0.05) * 2


def test_killer_instinct_grants_extra_turn():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    b = PlayerBase()
    b.hp = 10
    party.members.append(a)
    award_relic(party, "killer_instinct")
    apply_relics(party)
    BUS.emit("ultimate_used", a)
    turns: list[PlayerBase] = []
    BUS.subscribe("extra_turn", lambda m: turns.append(m))
    b.hp = 0
    BUS.emit("damage_taken", b, a, 10)
    BUS.emit("turn_end")
    assert turns == [a]


def test_travelers_charm_buff():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    attacker = PlayerBase()
    a.defense = 100
    a.mitigation = 100
    party.members.append(a)
    award_relic(party, "travelers_charm")
    apply_relics(party)
    BUS.emit("damage_taken", a, attacker, 10)
    BUS.emit("turn_start")
    assert a.defense == 100 + int(100 * 0.25)
    assert a.mitigation == 110
    BUS.emit("turn_end")
    assert a.defense == 100
    assert a.mitigation == 100


def test_timekeepers_hourglass_extra_turn():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    party.members.append(a)
    award_relic(party, "timekeepers_hourglass")
    apply_relics(party)
    turns: list[PlayerBase] = []
    BUS.subscribe("extra_turn", lambda m: turns.append(m))
    import random
    orig = random.random
    random.random = lambda: 0.0
    BUS.emit("turn_start")
    random.random = orig
    assert turns == [a]


def test_greed_engine_drains_and_rewards():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    a.hp = a.max_hp = 200
    party.members.append(a)
    award_relic(party, "greed_engine")
    apply_relics(party)
    BUS.emit("turn_start")
    assert a.hp == 200 - int(200 * 0.01)
    BUS.emit("gold_earned", 100)
    assert party.gold == int(100 * 0.5)


def test_greed_engine_stacks():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    a.hp = a.max_hp = 200
    party.members.append(a)
    award_relic(party, "greed_engine")
    award_relic(party, "greed_engine")
    apply_relics(party)
    BUS.emit("turn_start")
    assert a.hp == 200 - int(200 * (0.01 + 0.005))
    BUS.emit("gold_earned", 100)
    assert party.gold == int(100 * (0.5 + 0.25))


def test_stellar_compass_crit_bonus():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    a.atk = 100
    party.members.append(a)
    award_relic(party, "stellar_compass")
    apply_relics(party)
    BUS.emit("crit_hit", a, None, 0)
    assert a.atk == int(100 * 1.015)
    BUS.emit("gold_earned", 100)
    assert party.gold == int(100 * 0.015)


def test_stellar_compass_stacks():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    a.atk = 100
    party.members.append(a)
    award_relic(party, "stellar_compass")
    award_relic(party, "stellar_compass")
    apply_relics(party)
    BUS.emit("crit_hit", a, None, 0)
    assert a.atk == int(100 * (1.015 ** 2))
    BUS.emit("gold_earned", 100)
    assert party.gold == int(100 * 0.03)


def test_echoing_drum_repeats_attack():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    b = PlayerBase()
    b.hp = 100
    party.members.append(a)
    award_relic(party, "echoing_drum")
    apply_relics(party)
    BUS.emit("battle_start")
    b.hp -= 20
    BUS.emit("attack_used", a, b, 20)
    assert b.hp == 100 - 20 - int(20 * 0.25)
    b.hp -= 20
    BUS.emit("attack_used", a, b, 20)
    assert b.hp == 100 - 20 - int(20 * 0.25) - 20


def test_echoing_drum_stacks():
    event_bus_module.bus._subs.clear()
    party = Party()
    a = PlayerBase()
    b = PlayerBase()
    b.hp = 100
    party.members.append(a)
    award_relic(party, "echoing_drum")
    award_relic(party, "echoing_drum")
    apply_relics(party)
    BUS.emit("battle_start")
    b.hp -= 20
    BUS.emit("attack_used", a, b, 20)
    assert b.hp == 100 - 20 - int(20 * 0.25) * 2
