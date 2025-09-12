import asyncio
from unittest.mock import patch

from autofighter.cards import apply_cards
from autofighter.cards import award_card
from autofighter.effects import DamageOverTime
from autofighter.effects import EffectManager
from autofighter.party import Party
from autofighter.stats import BUS
from plugins.players._base import PlayerBase


def setup_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def test_overclock_double_action():
    loop = setup_event_loop()
    party = Party()
    ally = PlayerBase()
    foe = PlayerBase()
    ally.set_base_stat('atk', 100)
    foe.hp = foe.set_base_stat('max_hp', 1000)
    party.members.append(ally)
    award_card(party, "overclock")
    loop.run_until_complete(apply_cards(party))

    BUS.emit("battle_start", foe)
    BUS.emit("battle_start", ally)
    loop.run_until_complete(asyncio.sleep(0))
    expected = int(ally.atk * 2)
    assert foe.hp == 1000 - expected


def test_iron_resolve_revives_and_cooldown():
    party = Party()
    ally = PlayerBase()
    enemy = PlayerBase()
    ally.hp = ally.set_base_stat('max_hp', 100)
    party.members.append(ally)
    loop = setup_event_loop()
    award_card(party, "iron_resolve")
    loop.run_until_complete(apply_cards(party))

    ally.hp = 0
    BUS.emit("damage_taken", ally, enemy, 200)
    assert ally.hp == int(ally.max_hp * 0.30)

    ally.hp = 0
    BUS.emit("damage_taken", ally, enemy, 200)
    assert ally.hp == 0

    for _ in range(3):
        BUS.emit("turn_end")

    ally.hp = 0
    BUS.emit("damage_taken", ally, enemy, 200)
    assert ally.hp == int(ally.max_hp * 0.30)


def test_arcane_repeater_repeats_attack():
    loop = setup_event_loop()
    party = Party()
    ally = PlayerBase()
    foe = PlayerBase()
    ally.set_base_stat('atk', 100)
    foe.hp = foe.set_base_stat('max_hp', 1000)
    party.members.append(ally)
    award_card(party, "arcane_repeater")
    loop.run_until_complete(apply_cards(party))

    dmg = loop.run_until_complete(foe.apply_damage(ally.atk, attacker=ally))
    with patch("random.random", return_value=0.1):
        BUS.emit("attack_used", ally, foe, dmg)
        loop.run_until_complete(asyncio.sleep(0))
    expected = dmg + int(dmg * 0.5)
    assert foe.hp == 1000 - expected


def test_mindful_tassel_boosts_first_debuff():
    loop = setup_event_loop()
    party = Party()
    ally = PlayerBase()
    foe = PlayerBase()
    party.members.append(ally)
    award_card(party, "mindful_tassel")
    loop.run_until_complete(apply_cards(party))

    BUS.emit("battle_start", ally)
    BUS.emit("battle_start", foe)
    loop.run_until_complete(asyncio.sleep(0))

    mgr = EffectManager(foe)
    foe.effect_manager = mgr
    bleed = DamageOverTime(
        name="Bleed",
        damage=100,
        turns=10,
        id="bleed",
        source=ally,
    )
    mgr.add_dot(bleed)
    loop.run_until_complete(asyncio.sleep(0))
    assert bleed.damage == 105
    assert bleed.turns == 11

    poison = DamageOverTime(
        name="Poison",
        damage=100,
        turns=10,
        id="poison",
        source=ally,
    )
    mgr.add_dot(poison)
    loop.run_until_complete(asyncio.sleep(0))
    assert poison.damage == 100
    assert poison.turns == 10
