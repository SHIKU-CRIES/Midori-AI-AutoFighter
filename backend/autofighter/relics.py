from pathlib import Path
import random

from plugins import PluginLoader
from plugins.relics._base import RelicBase

from .party import Party

_loader: PluginLoader | None = None

def _registry() -> dict[str, type[RelicBase]]:
    global _loader
    if _loader is None:
        plugin_dir = Path(__file__).resolve().parents[1] / "plugins" / "relics"
        _loader = PluginLoader(required=["relic"])
        _loader.discover(str(plugin_dir))
    return _loader.get_plugins("relic")

def award_relic(party: Party, relic_id: str) -> RelicBase | None:
    relic_cls = _registry().get(relic_id)
    if relic_cls is None:
        return None
    party.relics.append(relic_id)
    return relic_cls()


def relic_choices(party: Party, stars: int, count: int = 3) -> list[RelicBase]:
    """Return up to `count` unique relic options the party doesn't own.

    Never returns duplicate relics. If fewer than `count` unique relics are
    available at the requested star level, the result will contain fewer items
    rather than repeating entries. The special fallback relic is excluded here
    and is injected by battle logic only when no card options exist.
    """
    relics = [cls() for cls in _registry().values()]
    # Exclude relics the party owns and the fallback essence from normal pools
    available = [
        r for r in relics
        if r.stars == stars and r.id not in party.relics and r.id != "fallback_essence"
    ]
    if not available:
        return []
    k = min(count, len(available))
    return random.sample(available, k=k)

def apply_relics(party: Party) -> None:
    registry = _registry()
    for rid in party.relics:
        relic_cls = registry.get(rid)
        if relic_cls:
            relic_cls().apply(party)
