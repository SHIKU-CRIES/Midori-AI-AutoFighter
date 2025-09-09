from __future__ import annotations

from typing import Any

from quart import Blueprint
from quart import jsonify

from autofighter.passives import discover as discover_passives
from autofighter.rooms.shop import PRICE_BY_STARS
from autofighter.rooms.shop import REROLL_COST
from plugins.damage_types import ALL_DAMAGE_TYPES
from plugins.damage_types import load_damage_type


bp = Blueprint("guidebook", __name__, url_prefix="/guidebook")


@bp.get("/damage-types")
async def damage_types() -> tuple[str, int, dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for name in ALL_DAMAGE_TYPES:
        inst = load_damage_type(name)
        cls = type(inst)
        desc = getattr(cls, "__doc__", None)
        if not desc:
            # Provide a concise fallback description
            weakness = getattr(inst, "weakness", None)
            tail = f" Weak to {weakness}." if weakness else ""
            desc = f"Elemental damage type.{tail}"
        entries.append(
            {
                "id": getattr(inst, "id", name),
                "weakness": getattr(inst, "weakness", None),
                "color": getattr(inst, "color", None),
                "description": str(desc).strip(),
            }
        )
    return jsonify({"damage_types": entries}), 200


@bp.get("/ultimates")
async def ultimates() -> tuple[str, int, dict[str, Any]]:
    info: list[dict[str, Any]] = []
    for name in ALL_DAMAGE_TYPES:
        inst = load_damage_type(name)
        cls = type(inst)
        # Try to extract docstring from ultimate implementation
        doc = getattr(cls.ultimate, "__doc__", None)  # type: ignore[attr-defined]
        if not doc:
            # Provide specific fallbacks for known types
            lowers = name.lower()
            if lowers == "lightning":
                doc = "AoE strike; applies random elemental DoTs; adds Aftertaste on hit."
            elif lowers == "light":
                doc = "Heal allies based on missing HP; reduce enemy defenses briefly."
            elif lowers == "dark":
                doc = "Multi-hit dark barrage scaling with DoT stacks; strong single-target damage."
            elif lowers == "wind":
                doc = "Rapid multi-hit across enemies; spreads on-hit interactions."
            elif lowers == "fire":
                doc = "AoE damage and inflict burns; gains temporary drain stacks on use."
            elif lowers == "ice":
                doc = "Strike all foes six times, increasing damage per target."
            else:
                doc = f"{name} ultimate ability."
        info.append({"id": getattr(inst, "id", name), "description": str(doc).strip()})
    return jsonify({"ultimates": info}), 200


@bp.get("/passives")
async def passives() -> tuple[str, int, dict[str, Any]]:
    registry = discover_passives()
    items: list[dict[str, Any]] = []
    for pid, cls in sorted(registry.items()):
        name = getattr(cls, "name", pid)
        trigger = getattr(cls, "trigger", None)
        doc = getattr(cls, "__doc__", "") or ""
        items.append(
            {
                "id": pid,
                "name": name,
                "trigger": trigger,
                "description": str(doc).strip(),
            }
        )
    return jsonify({"passives": items}), 200


@bp.get("/shops")
async def shops() -> tuple[str, int, dict[str, Any]]:
    return jsonify({
        "reroll_cost": REROLL_COST,
        "price_by_stars": PRICE_BY_STARS,
        "notes": [
            "Shop stock includes cards and relics; prices scale with pressure.",
            "Reroll generates a new stock list at a fixed gold cost.",
        ],
    }), 200


@bp.get("/ui")
async def ui() -> tuple[str, int, dict[str, Any]]:
    tips = [
        {"name": "Overlays", "description": "Open Settings, Inventory, and Guidebook from the main menu."},
        {"name": "Battle Review", "description": "After battles, view damage by type and proceed to the next room."},
        {"name": "Rewards", "description": "Choose cards, relics, and loot when available before advancing."},
    ]
    return jsonify({"tips": tips}), 200


@bp.get("/mechs")
async def mechs() -> tuple[str, int, dict[str, Any]]:
    mechanics = [
        {"name": "Ultimate Charge", "description": "Gain charge during combat; spend it to use your damage type's ultimate."},
        {"name": "DoTs & HoTs", "description": "Damage/Healing over time effects stack and interact with some elements."},
        {"name": "Enrage", "description": "Foes may gain enrage increasing difficulty as rooms progress."},
    ]
    return jsonify({"mechanics": mechanics}), 200
