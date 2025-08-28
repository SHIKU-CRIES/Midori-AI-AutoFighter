from __future__ import annotations

from collections import Counter
from dataclasses import fields
import math
import random
from typing import Any

from plugins import foes as foe_plugins
from plugins import players as player_plugins
from plugins.foes._base import FoeBase

from ..mapgen import MapNode
from ..party import Party
from ..stats import Stats


def _scale_stats(obj: Stats, node: MapNode, strength: float = 1.0) -> None:
    """Scale foe stats based on room metadata.

    Foes grow stronger with floor, room index, loop count, and user-set pressure.
    Small per-stat variation keeps battles from feeling identical.
    """
    starter_int = 1.0 + random.uniform(-0.05, 0.05)
    floor_mult = starter_int + 0.08 * max(node.floor - 1, 0)
    index_mult = starter_int + 0.10 * max(node.index - 1, 0)
    loop_mult = starter_int + 0.20 * max(node.loop - 1, 0)
    pressure_mult = 1.0 * max(node.pressure, 1)
    base_mult = max(strength * floor_mult * index_mult * loop_mult * pressure_mult, 0.5)

    # Apply a global pre-scale debuff to foes so they are significantly weaker
    # before room modifiers are applied. This reduces core combat stats by 10x.
    foe_debuff = 0.1 if isinstance(obj, FoeBase) else 1.0
    if foe_debuff != 1.0:
        try:
            if hasattr(obj, "atk") and isinstance(obj.atk, (int, float)):
                obj.atk = type(obj.atk)(obj.atk * foe_debuff)
        except Exception:
            pass
        try:
            if hasattr(obj, "defense") and isinstance(obj.defense, (int, float)):
                obj.defense = type(obj.defense)(obj.defense * foe_debuff)
        except Exception:
            pass
        try:
            if hasattr(obj, "max_hp") and isinstance(obj.max_hp, (int, float)):
                obj.max_hp = type(obj.max_hp)(obj.max_hp * foe_debuff)
            if hasattr(obj, "hp") and isinstance(obj.hp, (int, float)):
                obj.hp = type(obj.hp)(obj.hp * foe_debuff)
        except Exception:
            pass

    for field in fields(type(obj)):
        if field.name in {"exp", "level", "exp_multiplier"}:
            continue
        value = getattr(obj, field.name, None)
        if isinstance(value, (int, float)):
            per_stat_variation = 1.0 + random.uniform(-0.05, 0.05)
            total = value * base_mult * per_stat_variation
            setattr(obj, field.name, type(value)(total))

    try:
        room_num = max(int(node.index), 1)
        desired = max(1, math.ceil(room_num / 2))
        obj.level = int(max(getattr(obj, "level", 1), desired))
    except Exception:
        pass

    try:
        room_num = max(int(node.index), 1)
        # Keep the same base curve but apply foe debuff to the minimum target as well
        base_hp = int(700 * room_num * (foe_debuff if isinstance(obj, FoeBase) else 1.0))
        low = int(base_hp * 0.85)
        high = int(base_hp * 1.10)
        target = random.randint(low, max(high, low + 1))
        current_max = int(getattr(obj, "max_hp", 1))
        new_max = max(current_max, target)
        obj.max_hp = new_max
        obj.hp = new_max
    except Exception:
        pass

    try:
        cd = getattr(obj, "crit_damage", None)
        if isinstance(cd, (int, float)):
            obj.crit_damage = type(cd)(max(float(cd), 2.0))
    except Exception:
        pass

    # Enforce a minimum defense value for foes so they are not trivially zeroed.
    try:
        if isinstance(obj, FoeBase):
            d = getattr(obj, "defense", None)
            if isinstance(d, (int, float)):
                new_def = max(5, int(d))
                # For foes, 'defense' is a dataclass field; set the field directly
                try:
                    setattr(obj, "defense", type(d)(new_def))
                except Exception:
                    # As a fallback, adjust base stat
                    try:
                        obj.set_base_stat("defense", new_def)
                    except Exception:
                        pass
    except Exception:
        pass

    try:
        if isinstance(obj, FoeBase):
            vit = getattr(obj, "vitality", None)
            if isinstance(vit, (int, float)):
                thr = 0.5
                step = 0.25
                base_slow = 5.0
                fvit = float(vit)
                if fvit < thr:
                    fvit = thr
                else:
                    excess = fvit - thr
                    steps = int(excess // step)
                    factor = base_slow + steps
                    fvit = thr + (excess / factor)
                    fvit = max(fvit, thr)
                # Foes use dataclass fields, so set the live field directly
                try:
                    setattr(obj, "vitality", type(vit)(fvit))
                except Exception:
                    pass
    except Exception:
        pass

    try:
        if isinstance(obj, FoeBase):
            mit = getattr(obj, "mitigation", None)
            if isinstance(mit, (int, float)):
                thr = 0.2
                step = 0.01
                base_slow = 5.0
                fmit = float(mit)
                if fmit < thr:
                    fmit = thr
                else:
                    excess = fmit - thr
                    steps = int(excess // step)
                    factor = base_slow + steps
                    fmit = thr + (excess / factor)
                    fmit = max(fmit, thr)
                # Foes use dataclass fields, so set the live field directly
                try:
                    setattr(obj, "mitigation", type(mit)(fmit))
                except Exception:
                    pass
    except Exception:
        pass


def _normalize_damage_type(dt: Any) -> str:
    """Return a simple identifier for a damage type or element."""
    try:
        if isinstance(dt, str):
            return dt
        ident = getattr(dt, "id", None) or getattr(dt, "name", None)
        if ident:
            return str(ident)
        if isinstance(dt, dict):
            return str(dt.get("id") or dt.get("name") or "Generic")
    except Exception:
        pass
    return "Generic"


def _serialize(obj: Stats) -> dict[str, Any]:
    """Convert a stat object into a plain serializable dictionary.

    This function is intentionally defensive: if an unexpected object is
    encountered (e.g., ``None``), it returns a minimal fallback to keep the
    battle snapshot and UI resilient instead of raising.
    """
    if obj is None:
        return {
            "id": "unknown",
            "name": "Unknown",
            "hp": 0,
            "max_hp": 0,
            "passives": [],
            "dots": [],
            "hots": [],
            "damage_type": "Generic",
            "element": "Generic",
            "level": 1,
            "atk": 0,
            "defense": 0,
            "mitigation": 100,
            "crit_rate": 0.0,
            "crit_damage": 2.0,
            "effect_hit_rate": 0.0,
            "effect_resistance": 0.0,
            "shields": 0,
            "overheal_enabled": False,
        }

    # Build a dict without dataclasses.asdict to avoid deepcopy of complex fields
    try:
        data: dict[str, Any] = {}
        for f in fields(type(obj)):
            name = f.name
            if name == "lrm_memory":
                continue
            value = getattr(obj, name, None)
            if isinstance(value, (int, float, bool, str)) or value is None:
                data[name] = value
            elif isinstance(value, list):
                data[name] = list(value)
            elif isinstance(value, dict):
                data[name] = dict(value)
            else:
                data[name] = str(value)
    except Exception:
        # Non-dataclass object or serialization issue: build a minimal view
        norm = _normalize_damage_type(getattr(obj, "damage_type", None))
        return {
            "id": getattr(obj, "id", "unknown"),
            "name": getattr(obj, "name", getattr(obj, "id", "Unknown")),
            "hp": int(getattr(obj, "hp", 0) or 0),
            "max_hp": int(getattr(obj, "max_hp", 0) or 0),
            "passives": [],
            "dots": [],
            "hots": [],
            "damage_type": norm,
            "element": norm,
            "level": int(getattr(obj, "level", 1) or 1),
            "atk": int(getattr(obj, "atk", 0) or 0),
            "defense": int(getattr(obj, "defense", 0) or 0),
            "mitigation": getattr(obj, "mitigation", 100) or 100,
            "crit_rate": float(getattr(obj, "crit_rate", 0.0) or 0.0),
            "crit_damage": float(getattr(obj, "crit_damage", 2.0) or 2.0),
            "effect_hit_rate": float(getattr(obj, "effect_hit_rate", 0.0) or 0.0),
            "effect_resistance": float(getattr(obj, "effect_resistance", 0.0) or 0.0),
            "shields": int(getattr(obj, "shields", 0) or 0),
            "overheal_enabled": bool(getattr(obj, "overheal_enabled", False)),
        }

    # Remove non-serializable fields introduced by plugins (e.g., runtime memory)
    data.pop("lrm_memory", None)
    norm = _normalize_damage_type(getattr(obj, "damage_type", None))
    data["damage_type"] = norm
    data["element"] = norm
    data["id"] = obj.id
    if hasattr(obj, "name"):
        data["name"] = obj.name
    if hasattr(obj, "char_type"):
        data["char_type"] = getattr(obj.char_type, "value", obj.char_type)

    data.pop("dots", None)
    data.pop("hots", None)
    counts = Counter(data.pop("passives", []))
    data["passives"] = [{"id": pid, "stacks": count} for pid, count in counts.items()]

    mgr = getattr(obj, "effect_manager", None)
    dots = []
    hots = []
    if mgr is not None:
        def pack(effects, key):
            grouped: dict[str, dict[str, Any]] = {}
            for eff in effects:
                # Determine the elemental type for this effect from its source or attached type
                elem = "Generic"
                try:
                    src = getattr(eff, "source", None)
                    dtype = getattr(eff, "damage_type", None) or getattr(src, "damage_type", None)
                    elem = _normalize_damage_type(dtype)
                except Exception:
                    pass
                entry = grouped.setdefault(
                    eff.id,
                    {
                        "id": eff.id,
                        "name": eff.name,
                        key: getattr(eff, key),
                        "turns": eff.turns,
                        "source": getattr(getattr(eff, "source", None), "id", None),
                        "element": elem,
                        "stacks": 0,
                    },
                )
                entry["turns"] = max(entry["turns"], eff.turns)
                entry["stacks"] += 1
            return list(grouped.values())

        dots = pack(mgr.dots, "damage")
        hots = pack(mgr.hots, "healing")

    data["dots"] = dots
    data["hots"] = hots

    # Add special effects (aftertaste, crit boost, etc.)
    active_effects = []
    if hasattr(obj, '_active_effects'):
        for effect in obj.get_active_effects():
            active_effects.append({
                "name": effect.name,
                "source": effect.source,
                "duration": effect.duration,
                "modifiers": effect.stat_modifiers
            })
    data["active_effects"] = active_effects

    # Ensure in-run (runtime) stats are present even when implemented as @property
    # on the Stats dataclass. For foes (plain dataclasses), fall back to raw attrs.
    def _num(get, default=0):
        try:
            v = get()
            return v if isinstance(v, (int, float)) else default
        except Exception:
            return default

    if isinstance(obj, Stats):
        data["max_hp"] = int(_num(lambda: obj.max_hp, data.get("max_hp", 0)))
        data["atk"] = int(_num(lambda: obj.atk, data.get("atk", 0)))
        data["defense"] = int(_num(lambda: obj.defense, data.get("defense", 0)))
        data["crit_rate"] = float(_num(lambda: obj.crit_rate, data.get("crit_rate", 0.0)))
        data["crit_damage"] = float(_num(lambda: obj.crit_damage, data.get("crit_damage", 2.0)))
        data["effect_hit_rate"] = float(_num(lambda: obj.effect_hit_rate, data.get("effect_hit_rate", 0.0)))
        data["effect_resistance"] = float(_num(lambda: obj.effect_resistance, data.get("effect_resistance", 0.0)))
        data["mitigation"] = float(_num(lambda: obj.mitigation, data.get("mitigation", 1.0)))
        data["vitality"] = float(_num(lambda: obj.vitality, data.get("vitality", 1.0)))
        data["regain"] = int(_num(lambda: obj.regain, data.get("regain", 0)))
        data["dodge_odds"] = float(_num(lambda: obj.dodge_odds, data.get("dodge_odds", 0.0)))
        # Add shields/overheal support
        data["shields"] = int(_num(lambda: getattr(obj, "shields", 0), 0))
        data["overheal_enabled"] = bool(getattr(obj, "overheal_enabled", False))
    else:
        # Non-Stats objects: keep provided values if present
        data.setdefault("max_hp", int(getattr(obj, "max_hp", data.get("max_hp", 0)) or 0))
        data.setdefault("atk", int(getattr(obj, "atk", data.get("atk", 0)) or 0))
        data.setdefault("defense", int(getattr(obj, "defense", data.get("defense", 0)) or 0))
        data.setdefault("crit_rate", float(getattr(obj, "crit_rate", data.get("crit_rate", 0.0)) or 0.0))
        data.setdefault("crit_damage", float(getattr(obj, "crit_damage", data.get("crit_damage", 2.0)) or 2.0))
        data.setdefault("effect_hit_rate", float(getattr(obj, "effect_hit_rate", data.get("effect_hit_rate", 0.0)) or 0.0))
        data.setdefault("effect_resistance", float(getattr(obj, "effect_resistance", data.get("effect_resistance", 0.0)) or 0.0))
        data.setdefault("mitigation", float(getattr(obj, "mitigation", data.get("mitigation", 1.0)) or 1.0))
        data.setdefault("vitality", float(getattr(obj, "vitality", data.get("vitality", 1.0)) or 1.0))
        data.setdefault("regain", int(getattr(obj, "regain", data.get("regain", 0)) or 0))
        data.setdefault("dodge_odds", float(getattr(obj, "dodge_odds", data.get("dodge_odds", 0.0)) or 0.0))
        # Add shields/overheal support
        data.setdefault("shields", int(getattr(obj, "shields", 0) or 0))
        data.setdefault("overheal_enabled", bool(getattr(obj, "overheal_enabled", False)))

    return data


def _choose_foe(party: Party) -> FoeBase:
    """Select a foe class not already in the party."""
    party_ids = {p.id for p in party.members}
    candidates = [
        getattr(foe_plugins, name)
        for name in getattr(foe_plugins, "__all__", [])
        if getattr(foe_plugins, name).id not in party_ids
    ]
    for name in getattr(player_plugins, "__all__", []):
        player_cls = getattr(player_plugins, name)
        if player_cls.id in party_ids:
            continue
        foe_cls = foe_plugins.PLAYER_FOES.get(player_cls.id)
        if foe_cls and foe_cls not in candidates:
            candidates.append(foe_cls)
    if not candidates:
        candidates = [foe_plugins.Slime]
    foe_cls = random.choice(candidates)
    return foe_cls()


def _build_foes(node: MapNode, party: Party) -> list[FoeBase]:
    """Build a list of foes for the given room node."""
    count = min(10, 1 + node.pressure // 5)
    return [_choose_foe(party) for _ in range(count)]
