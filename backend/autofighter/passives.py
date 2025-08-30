from __future__ import annotations

from collections import Counter
from typing import Any
from typing import Optional

from plugins import passives as passive_plugins


class PassiveRegistry:
    def __init__(self) -> None:
        self._registry = {
            getattr(passive_plugins, name).id: getattr(passive_plugins, name)
            for name in getattr(passive_plugins, "__all__", [])
        }

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

    async def trigger_siphon(self, mezzy_target, allies: list) -> None:
        """Trigger siphon mechanics for Mezzy's passive."""
        counts = Counter(mezzy_target.passives)
        for pid, count in counts.items():
            cls = self._registry.get(pid)
            if pid != "mezzy_gluttonous_bulwark" or cls is None:
                continue

            passive_instance = cls()
            if hasattr(passive_instance, "siphon_from_allies"):
                stacks = min(count, getattr(cls, "max_stacks", count))
                for _ in range(stacks):
                    await passive_instance.siphon_from_allies(mezzy_target, allies)
