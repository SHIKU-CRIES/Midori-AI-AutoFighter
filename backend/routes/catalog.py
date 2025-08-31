from __future__ import annotations

from quart import Blueprint
from quart import jsonify

# Import plugin registries directly to build metadata
from autofighter.cards import _registry as card_registry
from autofighter.relics import _registry as relic_registry

bp = Blueprint("catalog", __name__, url_prefix="/catalog")


@bp.get("/cards")
async def list_cards():
    reg = card_registry()
    cards = []
    for cls in reg.values():
        try:
            c = cls()
            cards.append({
                "id": c.id,
                "name": c.name,
                "stars": c.stars,
                "about": getattr(c, "about", ""),
            })
        except Exception:
            # Skip malformed plugins rather than erroring the whole list
            continue
    return jsonify({"cards": cards})


@bp.get("/relics")
async def list_relics():
    reg = relic_registry()
    relics = []
    for cls in reg.values():
        try:
            r = cls()
            relics.append({
                "id": r.id,
                "name": r.name,
                "stars": r.stars,
                # Base about text; inventory display does not vary by stacks
                "about": getattr(r, "about", ""),
            })
        except Exception:
            continue
    return jsonify({"relics": relics})


@bp.get("/dots")
async def list_dots():
    dots = []
    # Manually import known DoT classes since they don't use a registry
    dot_classes = [
        ('bleed', 'Bleed', 'Deals damage over time based on max HP'),
        ('poison', 'Poison', 'Deals poison damage over time'),
        ('blazing_torment', 'Blazing Torment', 'Fire-based damage over time'),
        ('cold_wound', 'Cold Wound', 'Ice-based damage over time'),
        ('frozen_wound', 'Frozen Wound', 'Frozen damage over time'),
        ('abyssal_corruption', 'Abyssal Corruption', 'Dark corruption damage'),
        ('abyssal_weakness', 'Abyssal Weakness', 'Weakening dark effect'),
        ('celestial_atrophy', 'Celestial Atrophy', 'Light-based weakening'),
        ('charged_decay', 'Charged Decay', 'Electric decay damage'),
        ('gale_erosion', 'Gale Erosion', 'Wind-based erosion damage'),
        ('impact_echo', 'Impact Echo', 'Physical impact echo'),
        ('shadow_siphon', 'Shadow Siphon', 'Shadow damage that drains'),
        ('twilight_decay', 'Twilight Decay', 'Twilight element decay')
    ]

    for dot_id, name, description in dot_classes:
        dots.append({
            "id": dot_id,
            "name": name,
            "about": description
        })

    return jsonify({"dots": dots})


@bp.get("/hots")
async def list_hots():
    hots = []
    # Manually import known HoT classes since they don't use a registry
    hot_classes = [
        ('regeneration', 'Regeneration', 'Provides healing over time'),
        ('radiant_regeneration', 'Radiant Regeneration', 'Light-based healing over time'),
        ('player_heal', 'Player Heal', 'Basic player healing effect'),
        ('player_echo', 'Player Echo', 'Echo healing effect')
    ]

    for hot_id, name, description in hot_classes:
        hots.append({
            "id": hot_id,
            "name": name,
            "about": description
        })

    return jsonify({"hots": hots})

