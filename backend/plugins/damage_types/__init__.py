from __future__ import annotations

from importlib import import_module
from random import choice

from plugins.damage_types._base import DamageTypeBase

ALL_DAMAGE_TYPES = [
    "Light",
    "Dark",
    "Wind",
    "Lightning",
    "Fire",
    "Ice",
]


def _load_cls(name: str) -> type[DamageTypeBase]:
    try:
        module = import_module(f"plugins.damage_types.{name.lower()}")
        return getattr(module, name)
    except Exception:
        module = import_module("plugins.damage_types.generic")
        return module.Generic


def random_damage_type() -> DamageTypeBase:
    return _load_cls(choice(ALL_DAMAGE_TYPES))()


def get_damage_type(name: str) -> DamageTypeBase:
    lowered = name.lower()
    if "luna" in lowered:
        return _load_cls("Generic")()
    if "kboshi" in lowered:
        return _load_cls("Dark")()
    if "ixia" in lowered:
        return _load_cls("Lightning")()
    matches = [dtype for dtype in ALL_DAMAGE_TYPES if dtype.lower() in lowered]
    if matches:
        return _load_cls(choice(matches))()
    return random_damage_type()


def load_damage_type(name: str) -> DamageTypeBase:
    # Capitalize the first letter to match class names
    return _load_cls(name.capitalize())()


__all__ = [
    "ALL_DAMAGE_TYPES",
    "get_damage_type",
    "load_damage_type",
    "random_damage_type",
]
