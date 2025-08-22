from __future__ import annotations

from random import choice
from importlib import import_module

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
        return getattr(module, "Generic")


def random_damage_type() -> DamageTypeBase:
    return _load_cls(choice(ALL_DAMAGE_TYPES))()


def get_damage_type(name: str) -> DamageTypeBase:
    lowered = name.lower()
    if "luna" in lowered:
        return _load_cls("Generic")()
    matches = [dtype for dtype in ALL_DAMAGE_TYPES if dtype.lower() in lowered]
    if matches:
        return _load_cls(choice(matches))()
    return random_damage_type()


def load_damage_type(name: str) -> DamageTypeBase:
    return _load_cls(name)()


__all__ = [
    "ALL_DAMAGE_TYPES",
    "random_damage_type",
    "get_damage_type",
    "load_damage_type",
]
