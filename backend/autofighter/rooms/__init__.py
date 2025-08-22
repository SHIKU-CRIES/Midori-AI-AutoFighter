from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..mapgen import MapNode
from ..party import Party


@dataclass
class Room:
    """Base room type. Subclasses implement :meth:`resolve`."""

    node: MapNode

    async def resolve(self, party: Party, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


from .battle import BattleRoom  # noqa: E402
from .boss import BossRoom  # noqa: E402
from .rest import RestRoom  # noqa: E402
from .shop import ShopRoom  # noqa: E402
from .chat import ChatRoom  # noqa: E402
