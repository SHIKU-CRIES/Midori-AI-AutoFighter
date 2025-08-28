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
    relics = [cls() for cls in _registry().values()]
    # Exclude fallback relic from normal selection - it should only appear when no cards are available
    available = [r for r in relics if r.stars == stars and r.id not in party.relics and r.id != "fallback_essence"]
    if not available:
        return []
    if len(available) >= count:
        return random.sample(available, k=count)
    return random.choices(available, k=count)

def apply_relics(party: Party) -> None:
    registry = _registry()
    for rid in party.relics:
        relic_cls = registry.get(rid)
        if relic_cls:
            relic_cls().apply(party)
