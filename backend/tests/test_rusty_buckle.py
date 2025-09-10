import pytest

from autofighter.party import Party
import autofighter.stats as stats
from plugins.effects.aftertaste import Aftertaste
from plugins.event_bus import EventBus
from plugins.foes._base import FoeBase
from plugins.players._base import PlayerBase
from plugins.relics._base import safe_async_task
from plugins.relics.rusty_buckle import RustyBuckle


@pytest.fixture
def bus(monkeypatch):
    bus = EventBus()
    monkeypatch.setattr(stats, "BUS", bus)
    import plugins.relics.rusty_buckle as rb
    monkeypatch.setattr(rb, "BUS", bus)
    stats.set_battle_active(True)
    yield bus
    stats.set_battle_active(False)


def test_all_allies_bleed_each_turn(bus):
    party = Party(
        members=[PlayerBase(max_hp=1000, hp=1000), PlayerBase(max_hp=800, hp=800)],
        relics=["rusty_buckle"],
    )
    relic = RustyBuckle()
    relic.apply(party)
    foe = FoeBase()
    bus.emit("turn_start", foe)
    for member in party.members:
        bus.emit("turn_start", member)
    assert party.members[0].hp == 950
    assert party.members[1].hp == 760
    for member in party.members:
        bus.emit("turn_start", member)
    assert party.members[0].hp == 900
    assert party.members[1].hp == 720


def test_aftertaste_triggers_on_cumulative_loss(monkeypatch, bus):
    party = Party(
        members=[PlayerBase(max_hp=1000, hp=1000), PlayerBase(max_hp=1000, hp=1000)],
        relics=["rusty_buckle"],
    )
    relic = RustyBuckle()
    relic.apply(party)
    foe = FoeBase()
    bus.emit("turn_start", foe)
    for member in party.members:
        bus.emit("turn_start", member)

    hits = 0

    async def fake_apply(self, attacker, target):
        nonlocal hits
        hits += 1
        return []

    monkeypatch.setattr(Aftertaste, "apply", fake_apply)
    safe_async_task(party.members[0].apply_damage(950))
    assert hits == 0
    safe_async_task(party.members[1].apply_damage(950))
    assert hits == 5


def test_stacks_increase_threshold(monkeypatch, bus):
    party = Party(
        members=[PlayerBase(max_hp=1000, hp=1000), PlayerBase(max_hp=1000, hp=1000)],
        relics=["rusty_buckle", "rusty_buckle"],
    )
    relic = RustyBuckle()
    relic.apply(party)
    foe = FoeBase()
    bus.emit("turn_start", foe)
    for member in party.members:
        bus.emit("turn_start", member)

    hits = 0

    async def fake_apply(self, attacker, target):
        nonlocal hits
        hits += 1
        return []

    monkeypatch.setattr(Aftertaste, "apply", fake_apply)
    safe_async_task(party.members[0].apply_damage(900))
    safe_async_task(party.members[0].apply_healing(900))
    safe_async_task(party.members[0].apply_damage(1000))
    assert hits == 0
    safe_async_task(party.members[1].apply_damage(900))
    assert hits == 8
