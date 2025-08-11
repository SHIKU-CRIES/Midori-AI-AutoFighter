from __future__ import annotations

from random import choice

ALL_DAMAGE_TYPES = [
    "Light",
    "Dark",
    "Wind",
    "Lightning",
    "Fire",
    "Ice",
]


def random_damage_type() -> str:
    return choice(ALL_DAMAGE_TYPES)


def get_damage_type(name: str) -> str:
    lowered = name.lower()
    if "luna" in lowered:
        return "Generic"
    matches = [dtype for dtype in ALL_DAMAGE_TYPES if dtype.lower() in lowered]
    if matches:
        return choice(matches)
    return random_damage_type()
