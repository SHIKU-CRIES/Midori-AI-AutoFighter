from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
from typing import Optional

from plugins import PluginLoader

PASSIVE_LOADER: PluginLoader | None = None
PASSIVE_REGISTRY: dict[str, type] | None = None


def discover() -> dict[str, type]:
    """Load passive plugins once and return the registry."""
    global PASSIVE_LOADER
    global PASSIVE_REGISTRY

    if PASSIVE_REGISTRY is None:
        plugin_dir = Path(__file__).resolve().parents[1] / "plugins" / "passives"
        PASSIVE_LOADER = PluginLoader(required=["passive"])
        PASSIVE_LOADER.discover(str(plugin_dir))
        PASSIVE_REGISTRY = PASSIVE_LOADER.get_plugins("passive")
    assert PASSIVE_REGISTRY is not None
    return PASSIVE_REGISTRY


class PassiveRegistry:
    def __init__(self) -> None:
        self._registry = discover()

    async def trigger(self, event: str, target, **kwargs) -> None:
        """Trigger passives for a given event with optional context."""
        counts = Counter(target.passives)
        for pid, count in counts.items():
            cls = self._registry.get(pid)
            if cls is None or getattr(cls, "trigger", None) != event:
                continue
            stacks = min(count, getattr(cls, "max_stacks", count))
            for _ in range(stacks):
                await cls().apply(target)

    async def trigger_damage_taken(self, target, attacker: Optional[Any] = None, damage: int = 0) -> None:
        """Trigger passives specifically for damage taken events."""
        counts = Counter(target.passives)
        for pid, count in counts.items():
            cls = self._registry.get(pid)
            if cls is None or getattr(cls, "trigger", None) != "damage_taken":
                continue

            passive_instance = cls()

            # Special handling for counter-attack passives
            if hasattr(passive_instance, "counter_attack") and attacker is not None:
                stacks = min(count, getattr(cls, "max_stacks", count))
                for _ in range(stacks):
                    await passive_instance.counter_attack(target, attacker, damage)

            # Regular passive application
            stacks = min(count, getattr(cls, "max_stacks", count))
            for _ in range(stacks):
                await passive_instance.apply(target)

    async def trigger_turn_end(self, target) -> None:
        """Trigger turn end events for passives that need end-of-turn processing."""
        counts = Counter(target.passives)
        for pid, count in counts.items():
            cls = self._registry.get(pid)
            if cls is None:
                continue
            passive_instance = cls()

            # Check if passive has turn end handling
            if hasattr(passive_instance, "on_turn_end"):
                stacks = min(count, getattr(cls, "max_stacks", count))
                for _ in range(stacks):
                    await passive_instance.on_turn_end(target)

    async def trigger_defeat(self, target) -> None:
        """Trigger defeat events for passives that need cleanup on defeat."""
        counts = Counter(target.passives)
        for pid, count in counts.items():
            cls = self._registry.get(pid)
            if cls is None:
                continue
            passive_instance = cls()

            # Check if passive has defeat handling
            if hasattr(passive_instance, "on_defeat"):
                stacks = min(count, getattr(cls, "max_stacks", count))
                for _ in range(stacks):
                    await passive_instance.on_defeat(target)

    def describe(self, target) -> list[dict[str, Any]]:
        """Return structured information for a target's passives."""
        info: list[dict[str, Any]] = []
        counts = Counter(getattr(target, "passives", []))
        for pid, count in counts.items():
            cls = self._registry.get(pid)
            if cls is None:
                info.append({"id": pid, "name": pid, "stacks": count, "max_stacks": count})
                continue
            stacks = count
            if hasattr(cls, "get_stacks"):
                try:
                    stacks = cls.get_stacks(target)  # type: ignore[attr-defined]
                except Exception:
                    stacks = count
            max_stacks = getattr(cls, "max_stacks", stacks)
            info.append(
                {
                    "id": pid,
                    "name": getattr(cls, "name", pid),
                    "stacks": stacks,
                    "max_stacks": max_stacks,
                }
            )
        return info


