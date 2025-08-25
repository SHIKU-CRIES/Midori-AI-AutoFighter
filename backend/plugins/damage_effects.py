from __future__ import annotations

from typing import Callable, Dict, Optional

from autofighter.effects import DamageOverTime, HealingOverTime
from plugins.dots.abyssal_corruption import AbyssalCorruption
from plugins.dots.blazing_torment import BlazingTorment
from plugins.dots.celestial_atrophy import CelestialAtrophy
from plugins.dots.charged_decay import ChargedDecay
from plugins.dots.frozen_wound import FrozenWound
from plugins.dots.gale_erosion import GaleErosion
from plugins.dots.shadow_siphon import ShadowSiphon
from plugins.hots.radiant_regeneration import RadiantRegeneration


def _set_source(effect: DamageOverTime | HealingOverTime, source) -> object:
    effect.source = source
    return effect


DOT_FACTORIES: Dict[str, Callable[[float, object], DamageOverTime]] = {
    "Dark": lambda dmg, src: _set_source(AbyssalCorruption(int(dmg * 0.4), 3), src),
    "Fire": lambda dmg, src: _set_source(BlazingTorment(int(dmg * 0.5), 3), src),
    "Ice": lambda dmg, src: _set_source(FrozenWound(int(dmg * 0.25), 3), src),
    "Light": lambda dmg, src: _set_source(CelestialAtrophy(int(dmg * 0.3), 3), src),
    "Lightning": lambda dmg, src: _set_source(ChargedDecay(int(dmg * 0.25), 3), src),
    "Wind": lambda dmg, src: _set_source(GaleErosion(int(dmg * 0.25), 3), src),
}

HOT_FACTORIES: Dict[str, Callable[[object], HealingOverTime]] = {
    "Light": lambda src: _set_source(RadiantRegeneration(), src),
}


SHADOW_SIPHON_ID = ShadowSiphon.id


def create_shadow_siphon(damage: int, source) -> DamageOverTime:
    return _set_source(ShadowSiphon(damage), source)


def create_dot(damage_type: str, damage: float, source) -> Optional[DamageOverTime]:
    factory = DOT_FACTORIES.get(damage_type)
    if factory is None:
        return None
    return factory(damage, source)


def create_hot(damage_type: str, source) -> Optional[HealingOverTime]:
    factory = HOT_FACTORIES.get(damage_type)
    if factory is None:
        return None
    return factory(source)

