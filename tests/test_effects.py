import pathlib
import importlib.util

import pytest

from autofighter.stats import Stats
from autofighter.effects import EffectManager

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(cls_path: pathlib.Path, cls_name: str):
    spec = importlib.util.spec_from_file_location(cls_name, cls_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, cls_name)


Bleed = load(ROOT / "plugins/dots/bleed.py", "Bleed")
CelestialAtrophy = load(ROOT / "plugins/dots/celestial_atrophy.py", "CelestialAtrophy")
AbyssalCorruption = load(ROOT / "plugins/dots/abyssal_corruption.py", "AbyssalCorruption")
AbyssalWeakness = load(ROOT / "plugins/dots/abyssal_weakness.py", "AbyssalWeakness")
GaleErosion = load(ROOT / "plugins/dots/gale_erosion.py", "GaleErosion")
ChargedDecay = load(ROOT / "plugins/dots/charged_decay.py", "ChargedDecay")
FrozenWound = load(ROOT / "plugins/dots/frozen_wound.py", "FrozenWound")
BlazingTorment = load(ROOT / "plugins/dots/blazing_torment.py", "BlazingTorment")
ColdWound = load(ROOT / "plugins/dots/cold_wound.py", "ColdWound")
TwilightDecay = load(ROOT / "plugins/dots/twilight_decay.py", "TwilightDecay")
ImpactEcho = load(ROOT / "plugins/dots/impact_echo.py", "ImpactEcho")
Regeneration = load(ROOT / "plugins/hots/regeneration.py", "Regeneration")
PlayerEcho = load(ROOT / "plugins/hots/player_echo.py", "PlayerEcho")
PlayerHeal = load(ROOT / "plugins/hots/player_heal.py", "PlayerHeal")


DOT_CLASSES = [
    Bleed,
    CelestialAtrophy,
    AbyssalCorruption,
    AbyssalWeakness,
    GaleErosion,
    ChargedDecay,
    FrozenWound,
    BlazingTorment,
    ColdWound,
    TwilightDecay,
    ImpactEcho,
]


@pytest.mark.parametrize("dot_cls", DOT_CLASSES)
def test_dots_apply_damage(dot_cls):
    stats = Stats(hp=100, max_hp=100)
    manager = EffectManager(stats)
    manager.add_dot(dot_cls(damage=10, turns=1))
    manager.tick()
    assert stats.hp == 90
    assert manager.dots == []


def test_cold_wound_stack_cap():
    stats = Stats(hp=100, max_hp=100)
    manager = EffectManager(stats)
    for _ in range(6):
        manager.add_dot(
            ColdWound(damage=1, turns=1), max_stacks=ColdWound.max_stacks
        )
    assert len(manager.dots) == ColdWound.max_stacks


@pytest.mark.parametrize("hot_cls", [Regeneration])
def test_hots_apply_healing(hot_cls):
    stats = Stats(hp=50, max_hp=100)
    manager = EffectManager(stats)
    manager.add_hot(hot_cls(healing=10, turns=1))
    manager.tick()
    assert stats.hp == 60
    assert manager.hots == []


def test_player_named_hots():
    echo = PlayerEcho("Alice", healing=5, turns=1)
    heal = PlayerHeal("Bob", healing=5, turns=1)
    assert "Alice" in echo.name
    assert "Bob" in heal.name
