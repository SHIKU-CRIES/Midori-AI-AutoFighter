import asyncio
import importlib

from autofighter.effects import DamageOverTime
from autofighter.effects import EffectManager
from autofighter.stats import BUS
from autofighter.stats import Stats
import plugins.damage_types.dark as dark_module
import plugins.event_bus as event_bus_module


class DummyPlayer(Stats):
    def use_ultimate(self) -> bool:
        if not self.ultimate_ready:
            return False
        self.ultimate_charge = 0
        self.ultimate_ready = False
        BUS.emit("ultimate_used", self)
        return True


def _reload_dark():
    return importlib.reload(dark_module).Dark


def test_dark_ultimate_dot_scaling(monkeypatch):
    event_bus_module.bus._subs.clear()
    Dark = _reload_dark()

    actor = DummyPlayer()
    actor.damage_type = Dark()
    actor._base_atk = 100
    actor.ultimate_ready = True

    ally = Stats()
    actor.effect_manager = EffectManager(actor)
    ally.effect_manager = EffectManager(ally)
    actor.effect_manager.add_dot(DamageOverTime("d1", 1, 1, "d1"))
    ally.effect_manager.add_dot(DamageOverTime("d2", 1, 1, "d2"))

    target = Stats()
    actor.allies = [actor, ally]
    actor.enemies = [target]

    async def fake_apply_damage(self, amount, attacker=None, *, trigger_on_hit=True):
        return amount

    monkeypatch.setattr(Stats, "apply_damage", fake_apply_damage, raising=False)

    hits: list[int] = []
    BUS.subscribe("damage", lambda a, t, d: hits.append(d))

    actor.use_ultimate()
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))

    expected = int(100 * (1.75 ** 2))
    assert hits and all(h == expected for h in hits)


def test_dark_ultimate_six_hits(monkeypatch):
    event_bus_module.bus._subs.clear()
    Dark = _reload_dark()

    actor = DummyPlayer()
    actor.damage_type = Dark()
    actor._base_atk = 100
    actor.ultimate_ready = True

    target = Stats()
    actor.allies = [actor]
    actor.enemies = [target]

    async def fake_apply_damage(self, amount, attacker=None, *, trigger_on_hit=True):
        return amount

    monkeypatch.setattr(Stats, "apply_damage", fake_apply_damage, raising=False)

    hits: list[int] = []
    BUS.subscribe("damage", lambda a, t, d: hits.append(d))

    actor.use_ultimate()
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))

    assert len(hits) == 6
