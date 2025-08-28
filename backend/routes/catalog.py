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

