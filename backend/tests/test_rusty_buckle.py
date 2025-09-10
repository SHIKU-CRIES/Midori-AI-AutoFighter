import sys
import types

import pytest

from autofighter.party import Party
import autofighter.stats as stats
from plugins.effects.aftertaste import Aftertaste
from plugins.event_bus import EventBus
from plugins.foes._base import FoeBase
from plugins.players._base import PlayerBase
import plugins.relics.rusty_buckle as rb
from plugins.relics.rusty_buckle import RustyBuckle


@pytest.fixture
def bus(monkeypatch):
    bus = EventBus()
    bus._prefer_async = False
    monkeypatch.setattr(stats, "BUS", bus)
    monkeypatch.setattr(rb, "BUS", bus)
    llms = types.ModuleType("llms")
    torch_checker = types.ModuleType("llms.torch_checker")
    torch_checker.is_torch_available = lambda: False
    llms.torch_checker = torch_checker
    monkeypatch.setitem(sys.modules, "llms", llms)
    monkeypatch.setitem(sys.modules, "llms.torch_checker", torch_checker)

    def simple_damage(self, amount, attacker=None, **kwargs):
        self.hp = max(self.hp - int(amount), 0)
        bus.emit("damage_taken", self, attacker, amount)
        return int(amount)

    def simple_heal(self, amount, healer=None):
        self.hp = min(self.hp + int(amount), self.max_hp)
        bus.emit("heal_received", self, healer, amount)
        return int(amount)

    monkeypatch.setattr(PlayerBase, "apply_damage", simple_damage)
    monkeypatch.setattr(PlayerBase, "apply_healing", simple_heal)

    stats.set_battle_active(True)
    yield bus
    stats.set_battle_active(False)


def test_all_allies_bleed_each_turn(bus):
    first = PlayerBase()
    second = PlayerBase()
    second._base_max_hp = 800
    second.hp = 800
    party = Party(members=[first, second], relics=["rusty_buckle"])
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
    party = Party(members=[PlayerBase(), PlayerBase()], relics=["rusty_buckle"])
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
    party.members[0].apply_damage(1000)
    assert hits == 0
    party.members[1].apply_damage(1000)
    assert hits == 5


def test_stacks_increase_threshold(monkeypatch, bus):
    first = PlayerBase()
    second = PlayerBase()
    first._base_max_hp = 500
    first.hp = 500
    second._base_max_hp = 500
    second.hp = 500
    party = Party(members=[first, second], relics=["rusty_buckle", "rusty_buckle"])
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
    party.members[0].apply_damage(500)
    party.members[0].apply_healing(500)
    party.members[0].apply_damage(500)
    assert hits == 0
    party.members[1].apply_damage(500)
    assert hits == 8


def test_apply_no_type_error(bus):
    party = Party(members=[PlayerBase(), PlayerBase()], relics=["rusty_buckle"])
    relic = RustyBuckle()
    relic.apply(party)
