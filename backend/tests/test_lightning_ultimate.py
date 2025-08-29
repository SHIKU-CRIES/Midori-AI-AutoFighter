import asyncio
import random

import pytest

from autofighter.effects import EffectManager
from autofighter.stats import BUS
from autofighter.stats import Stats
from plugins.damage_types.lightning import Lightning
from plugins.dots.abyssal_corruption import AbyssalCorruption
from plugins.dots.blazing_torment import BlazingTorment
from plugins.dots.celestial_atrophy import CelestialAtrophy
from plugins.dots.charged_decay import ChargedDecay
from plugins.dots.frozen_wound import FrozenWound
from plugins.dots.gale_erosion import GaleErosion
from plugins.effects.aftertaste import Aftertaste


def test_lightning_ultimate_applies_random_dots(monkeypatch):
    lightning = Lightning()
    attacker = Stats()
    attacker._base_atk = 100
    attacker.damage_type = lightning
    target = Stats()
    target.effect_manager = EffectManager(target)

    types = ["Fire", "Ice", "Wind", "Lightning", "Light", "Dark"]
    seq = iter(types * 2)
    monkeypatch.setattr(random, "choice", lambda _seq: next(seq))

    lightning.ultimate(attacker, target)

    dot_map = {
        "Fire": BlazingTorment.id,
        "Ice": FrozenWound.id,
        "Wind": GaleErosion.id,
        "Lightning": ChargedDecay.id,
        "Light": CelestialAtrophy.id,
        "Dark": AbyssalCorruption.id,
    }
    expected = [dot_map[t] for t in types * 2][:10]
    assert [d.id for d in target.effect_manager.dots] == expected


@pytest.mark.asyncio
async def test_lightning_ultimate_aftertaste_stacks(monkeypatch):
    lightning = Lightning()
    attacker = Stats()
    attacker._base_atk = 100
    attacker.damage_type = lightning
    target = Stats()
    target.effect_manager = EffectManager(target)

    hits: list[int] = []

    async def fake_apply(self, atk, tgt):
        hits.append(self.hits)
        return [0] * self.hits

    monkeypatch.setattr(Aftertaste, "apply", fake_apply)

    lightning.ultimate(attacker, target)
    BUS.emit("hit_landed", attacker, target, 10)
    await asyncio.sleep(0)
    assert hits == [1]

    lightning.ultimate(attacker, target)
    BUS.emit("hit_landed", attacker, target, 10)
    await asyncio.sleep(0)
    BUS.emit("hit_landed", attacker, target, 10)
    await asyncio.sleep(0)
    assert hits == [1, 2, 2]

    BUS.emit("battle_end", attacker)
    BUS.emit("hit_landed", attacker, target, 10)
    await asyncio.sleep(0)
    assert hits == [1, 2, 2]

    lightning.ultimate(attacker, target)
    BUS.emit("hit_landed", attacker, target, 10)
    await asyncio.sleep(0)
    assert hits == [1, 2, 2, 1]
