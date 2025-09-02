from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from random import Random
from typing import ClassVar


@dataclass
class MapNode:
    room_id: int
    room_type: str
    floor: int
    index: int
    loop: int
    pressure: int

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> MapNode:
        # Provide default values for missing fields to handle legacy data
        return cls(
            room_id=data.get('room_id', 0),
            room_type=data.get('room_type', 'battle-weak'),
            floor=data.get('floor', 1),
            index=data.get('index', 0),
            loop=data.get('loop', 1),
            pressure=data.get('pressure', 0)
        )


class MapGenerator:
    rooms_per_floor: ClassVar[int] = 45

    def __init__(self, seed: str, floor: int = 1, loop: int = 1, pressure: int = 0) -> None:
        self._rand = Random(seed)
        self.floor = floor
        self.loop = loop
        self.pressure = pressure

    def generate_floor(self) -> list[MapNode]:
        nodes: list[MapNode] = []
        index = 0
        nodes.append(
            MapNode(
                room_id=index,
                room_type="start",
                floor=self.floor,
                index=index,
                loop=self.loop,
                pressure=self.pressure,
            )
        )
        index += 1
        middle = self.rooms_per_floor - 2
        quotas = {"shop": 2, "rest": 2}
        room_types: list[str] = []
        for key, count in quotas.items():
            room_types.extend([key] * count)
        battle_count = middle - sum(quotas.values())
        weak = battle_count // 2
        normal = battle_count - weak
        room_types.extend(["battle-weak"] * weak)
        room_types.extend(["battle-normal"] * normal)
        self._rand.shuffle(room_types)
        first_shop = room_types.index("shop") if "shop" in room_types else -1
        rest_indices = [i for i, rt in enumerate(room_types) if rt == "rest"]
        if first_shop >= 0 and rest_indices and max(rest_indices) < first_shop:
            swap_index = rest_indices[-1]
            for i in range(first_shop + 1, len(room_types)):
                if room_types[i] != "shop":
                    room_types[i], room_types[swap_index] = room_types[swap_index], room_types[i]
                    break
        if room_types and room_types[0] in {"shop", "rest"}:
            for i, rt in enumerate(room_types[1:], start=1):
                if rt not in {"shop", "rest"}:
                    room_types[0], room_types[i] = room_types[i], room_types[0]
                    break
        for rt in room_types:
            nodes.append(
                MapNode(
                    room_id=index,
                    room_type=rt,
                    floor=self.floor,
                    index=index,
                    loop=self.loop,
                    pressure=self.pressure,
                )
            )
            index += 1
        nodes.append(
            MapNode(
                room_id=index,
                room_type="battle-boss-floor",
                floor=self.floor,
                index=index,
                loop=self.loop,
                pressure=self.pressure,
            )
        )
        return nodes
