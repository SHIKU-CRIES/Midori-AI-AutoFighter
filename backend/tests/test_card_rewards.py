import asyncio
import importlib.util
import json
from pathlib import Path
import sys

import pytest
import sqlcipher3

import autofighter.cards as cards_module
from autofighter.cards import award_card
from autofighter.party import Party

sys.path.append(str(Path(__file__).resolve().parents[1]))
import autofighter.rooms.battle as rooms_module
from autofighter.stats import BUS
from autofighter.stats import Stats
from plugins.effects.critical_boost import CriticalBoost
from plugins.players._base import PlayerBase

NEW_CARDS: list[tuple[str, dict[str, float]]] = [
    ("lightweight_boots", {"dodge_odds": 0.03}),
    ("steel_bangles", {"mitigation": 0.03}),
    ("enduring_charm", {"vitality": 0.03}),
    ("keen_goggles", {"crit_rate": 0.03, "effect_hit_rate": 0.03}),
    ("honed_point", {"atk": 0.04}),
    ("fortified_plating", {"defense": 0.04}),
    ("rejuvenating_tonic", {"regain": 0.04}),
    ("adamantine_band", {"max_hp": 0.04}),
    ("precision_sights", {"crit_damage": 0.04}),
    ("inspiring_banner", {"atk": 0.02, "defense": 0.02}),
    ("tactical_kit", {"atk": 0.02, "max_hp": 0.02}),
    ("bulwark_totem", {"defense": 0.02, "max_hp": 0.02}),
    ("farsight_scope", {"crit_rate": 0.03}),
    ("steady_grip", {"atk": 0.03, "dodge_odds": 0.03}),
    ("coated_armor", {"mitigation": 0.03, "defense": 0.03}),
    ("swift_bandanna", {"crit_rate": 0.03, "dodge_odds": 0.03}),
    ("reinforced_cloak", {"defense": 0.03, "effect_resistance": 0.03}),
    ("vital_core", {"vitality": 0.03, "max_hp": 0.03}),
    ("enduring_will", {"mitigation": 0.03, "vitality": 0.03}),
    ("guardian_shard", {"defense": 0.02, "mitigation": 0.02}),
    ("sturdy_boots", {"dodge_odds": 0.03, "defense": 0.03}),
    ("spiked_shield", {"atk": 0.03, "defense": 0.03}),
    ("critical_focus", {"atk": 0.55}),
    ("critical_transfer", {}),
    ("iron_guard", {"defense": 0.55}),
    ("swift_footwork", {}),
    ("mystic_aegis", {"effect_resistance": 0.55}),
    ("vital_surge", {"max_hp": 0.55}),
    ("elemental_spark", {"atk": 0.55, "effect_hit_rate": 0.55}),
]

@pytest.fixture()
def app_with_db(tmp_path, monkeypatch):
    db_path = tmp_path / "save.db"
    monkeypatch.setenv("AF_DB_PATH", str(db_path))
    monkeypatch.setenv("AF_DB_KEY", "testkey")
    monkeypatch.syspath_prepend(Path(__file__).resolve().parents[1])
    spec = importlib.util.spec_from_file_location(
        "app", Path(__file__).resolve().parents[1] / "app.py",
    )
    app_module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(app_module)
    app_module.app.testing = True
    return app_module.app, db_path


def test_award_card_unique():
    member = Stats()
    member.id = "m1"
    party = Party(members=[member])
    assert award_card(party, "micro_blade") is not None
    assert award_card(party, "micro_blade") is None
    assert party.cards == ["micro_blade"]


@pytest.mark.asyncio
async def test_battle_offers_choices_and_applies_effect(app_with_db, monkeypatch):
    app, db_path = app_with_db
    client = app.test_client()

    start_resp = await client.post("/run/start", json={"party": ["player"]})
    run_id = (await start_resp.get_json())["run_id"]
    await client.put(f"/party/{run_id}", json={"party": ["player"]})

    monkeypatch.setattr(cards_module.random, "sample", lambda seq, k: list(seq)[:k])

    monkeypatch.setattr(rooms_module.random, "random", lambda: 0.0)
    battle_resp = await client.post(f"/rooms/{run_id}/battle")
    data = await battle_resp.get_json()
    assert data["party"][0]["atk"] == 100
    if not data["card_choices"]:
        pytest.skip("no card choices returned")
    chosen = data["card_choices"][0]["id"]
    assert data["card_choices"][0]["stars"] == 1
    assert "about" in data["card_choices"][0]

    await client.post(f"/cards/{run_id}", json={"card": chosen})
    await client.post(f"/run/{run_id}/next")
    while True:
        map_resp = await client.get(f"/map/{run_id}")
        map_state = (await map_resp.get_json())["map"]
        node = map_state["rooms"][map_state["current"]]
        room_type = node["room_type"]
        if room_type in {"battle-weak", "battle-normal"}:
            break
        if room_type == "shop":
            await client.post(f"/rooms/{run_id}/shop")
            await client.post(f"/run/{run_id}/next")
        elif room_type == "rest":
            await client.post(f"/rooms/{run_id}/rest")
            await client.post(f"/run/{run_id}/next")
        else:
            raise AssertionError(f"unexpected room type: {room_type}")

    battle_resp2 = await client.post(f"/rooms/{run_id}/battle")
    data2 = await battle_resp2.get_json()
    atk = next(p for p in data2["party"] if p["id"] == "player")["atk"]
    effect = cards_module._registry()[chosen]().effects.get("atk", 0)
    assert atk == int(100 * (1 + effect))

    conn = sqlcipher3.connect(db_path)
    conn.execute("PRAGMA key = 'testkey'")
    row = conn.execute("SELECT party FROM runs WHERE id = ?", (run_id,)).fetchone()
    saved = json.loads(row[0])
    assert chosen in saved["cards"]


@pytest.mark.parametrize("card_id,effects", NEW_CARDS)
@pytest.mark.asyncio
async def test_award_and_apply_new_cards(card_id, effects):
    member = Stats()
    member.id = "m1"
    party = Party(members=[member])
    baseline = {attr: getattr(member, attr) for attr in effects}
    assert award_card(party, card_id) is not None
    await cards_module.apply_cards(party)
    await asyncio.sleep(0)
    for attr, pct in effects.items():
        value = getattr(member, attr)
        expected = type(baseline[attr])(baseline[attr] * (1 + pct))
        assert value == expected
        if attr == "max_hp":
            assert member.hp == expected


@pytest.mark.asyncio
async def test_critical_focus_grants_boost():
    member = Stats()
    party = Party(members=[member])
    award_card(party, "critical_focus")
    await cards_module.apply_cards(party)
    await asyncio.sleep(0)
    base_rate = member.crit_rate
    base_dmg = member.crit_damage
    BUS.emit("turn_start")
    assert member.set_base_stat('crit_rate', = pytest.approx(base_rate + 0.005))
    assert member.set_base_stat('crit_damage', = pytest.approx(base_dmg + 0.05))
    BUS.emit("damage_taken", member, None, 10)
    assert member.set_base_stat('crit_rate', = pytest.approx(base_rate))


@pytest.mark.asyncio
async def test_critical_transfer_moves_stacks():
    a = PlayerBase()
    b = PlayerBase()
    party = Party(members=[a, b])
    award_card(party, "critical_transfer")
    await cards_module.apply_cards(party)
    await asyncio.sleep(0)
    cb_a = CriticalBoost()
    cb_a.apply(a)
    cb_a.apply(a)
    setattr(a, "_critical_boost", cb_a)
    cb_b = CriticalBoost()
    cb_b.apply(b)
    setattr(b, "_critical_boost", cb_b)
    base_atk = a.atk
    a.add_ultimate_charge(15)
    a.use_ultimate()
    await asyncio.sleep(0)
    assert getattr(a, "_critical_boost").stacks == 3
    assert a.set_base_stat('atk', = int(base_atk * 1.12))


@pytest.mark.asyncio
async def test_iron_guard_defense_buff():
    a = Stats()
    b = Stats()
    party = Party(members=[a, b])
    award_card(party, "iron_guard")
    await cards_module.apply_cards(party)
    await asyncio.sleep(0)
    base_a = a.defense
    base_b = b.defense
    BUS.emit("damage_taken", a, b, 10)
    assert a.set_base_stat('defense', = base_a + 20)
    assert b.set_base_stat('defense', = base_b + 20)


@pytest.mark.asyncio
async def test_swift_footwork_first_action(monkeypatch):
    member = Stats()
    member.action_points = 1
    party = Party(members=[member])
    award_card(party, "swift_footwork")
    await cards_module.apply_cards(party)
    await asyncio.sleep(0)
    assert member.actions_per_turn == 2
    events: list[str] = []

    def _listener(card_id, *_args):
        if card_id == "swift_footwork":
            events.append(_args[1])

    BUS.subscribe("card_effect", _listener)
    BUS.emit("battle_start")
    member.action_points -= 1
    BUS.emit("action_used", member, None, 10)
    await asyncio.sleep(0.05)
    assert member.action_points == 1
    member.action_points -= 1
    BUS.emit("action_used", member, None, 10)
    await asyncio.sleep(0.05)
    BUS.unsubscribe("card_effect", _listener)
    assert member.action_points == 0
    assert events.count("free_action") == 1


@pytest.mark.asyncio
async def test_mystic_aegis_heals_on_resist():
    member = Stats()
    member.hp = 800
    party = Party(members=[member])
    award_card(party, "mystic_aegis")
    await cards_module.apply_cards(party)
    await asyncio.sleep(0)
    BUS.emit("debuff_resisted", member)
    await asyncio.sleep(0)
    assert member.hp == 800 + int(member.max_hp * 0.05)


@pytest.mark.asyncio
async def test_vital_surge_low_hp_bonus():
    member = Stats()
    party = Party(members=[member])
    award_card(party, "vital_surge")
    await cards_module.apply_cards(party)
    await asyncio.sleep(0)
    assert member.set_base_stat('max_hp', = int(1000 * 1.55))
    member.hp = int(member.max_hp * 0.4)
    BUS.emit("turn_start")
    assert member.set_base_stat('atk', = int(200 * 1.55))
    member.hp = member.max_hp
    BUS.emit("heal_received", member, member, 100)
    assert member.set_base_stat('atk', = 200)


@pytest.mark.asyncio
async def test_elemental_spark_selects_ally(monkeypatch):
    member = Stats()
    party = Party(members=[member])
    award_card(party, "elemental_spark")
    await cards_module.apply_cards(party)
    await asyncio.sleep(0)
    base = member.effect_hit_rate

    import random

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    BUS.emit("battle_start")
    assert member.set_base_stat('effect_hit_rate', = pytest.approx(base + 0.05))
    BUS.emit("battle_end")
    await asyncio.sleep(0)
    assert member.set_base_stat('effect_hit_rate', = pytest.approx(base))
