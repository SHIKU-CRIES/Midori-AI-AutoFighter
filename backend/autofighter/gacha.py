from __future__ import annotations

from dataclasses import dataclass
import random
import time
from typing import Any

from plugins import players as player_plugins
from plugins.damage_types import ALL_DAMAGE_TYPES

from .save_manager import SaveManager


def _build_pools() -> tuple[list[str], list[str]]:
    five: list[str] = []
    six: list[str] = []
    for name in getattr(player_plugins, "__all__", []):
        cls = getattr(player_plugins, name)
        rarity = getattr(cls, "gacha_rarity", 0)
        cid = getattr(cls, "id", name)
        if cid in {"player", "luna", "mimic"}:
            continue
        if rarity == 5:
            five.append(cid)
        elif rarity == 6:
            six.append(cid)
    return five, six


FIVE_STAR, SIX_STAR = _build_pools()
ELEMENTS = [e.lower() for e in ALL_DAMAGE_TYPES]


@dataclass
class PullResult:
    type: str
    id: str
    rarity: int
    stacks: int | None = None


@dataclass
class Banner:
    id: str
    name: str
    banner_type: str  # "custom" or "standard"
    featured_character: str | None = None
    start_time: float = 0.0
    end_time: float = 0.0
    active: bool = True


class GachaManager:
    def __init__(self, save: SaveManager) -> None:
        self.save = save
        with self.save.connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS player_stacks (id TEXT PRIMARY KEY, stacks INTEGER NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS banners (id TEXT PRIMARY KEY, name TEXT, banner_type TEXT, featured_character TEXT, start_time REAL, end_time REAL, active INTEGER)"
            )
        self._init_default_banners()

    def _init_default_banners(self) -> None:
        """Initialize default banners if they don't exist."""
        current_time = time.time()

        with self.save.connection() as conn:
            # Check if banners already exist
            cur = conn.execute("SELECT COUNT(*) FROM banners")
            if cur.fetchone()[0] > 0:
                return

            # Create default banners
            banners = [
                Banner("standard", "Standard Warp", "standard", None, 0, 0, True),
                Banner("custom1", "Featured Character I", "custom", "becca", current_time, current_time + 86400 * 3, True),  # 3 days
                Banner("custom2", "Featured Character II", "custom", "ally", current_time + 86400 * 3, current_time + 86400 * 6, True),  # Next 3 days
            ]

            for banner in banners:
                conn.execute(
                    "INSERT INTO banners (id, name, banner_type, featured_character, start_time, end_time, active) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (banner.id, banner.name, banner.banner_type, banner.featured_character, banner.start_time, banner.end_time, 1 if banner.active else 0)
                )

    def get_banners(self) -> list[Banner]:
        """Get all available banners."""
        with self.save.connection() as conn:
            cur = conn.execute("SELECT id, name, banner_type, featured_character, start_time, end_time, active FROM banners ORDER BY banner_type, id")
            banners = []
            for row in cur.fetchall():
                banners.append(Banner(
                    id=row[0],
                    name=row[1],
                    banner_type=row[2],
                    featured_character=row[3],
                    start_time=row[4],
                    end_time=row[5],
                    active=bool(row[6])
                ))
            return banners

    def get_active_banner(self, banner_id: str) -> Banner | None:
        """Get a specific active banner."""
        banners = self.get_banners()
        current_time = time.time()

        for banner in banners:
            if banner.id == banner_id and banner.active:
                if banner.banner_type == "standard":
                    return banner
                elif banner.start_time <= current_time <= banner.end_time:
                    return banner
        return None

    def get_available_banners(self) -> list[Banner]:
        """Get all currently available banners."""
        banners = self.get_banners()
        current_time = time.time()
        available = []

        for banner in banners:
            if banner.active:
                if banner.banner_type == "standard":
                    available.append(banner)
                elif banner.start_time <= current_time <= banner.end_time:
                    available.append(banner)

        return available

    def get_featured_characters(self) -> list[dict[str, Any]]:
        """Get character information for all featured characters in active banners."""
        banners = self.get_available_banners()
        featured_chars = []

        for banner in banners:
            if banner.featured_character:
                # Get character info
                for name in getattr(player_plugins, "__all__", []):
                    cls = getattr(player_plugins, name)
                    if getattr(cls, "id", name) == banner.featured_character:
                        featured_chars.append({
                            "id": banner.featured_character,
                            "name": getattr(cls, "name", banner.featured_character),
                            "about": getattr(cls, "about", "Character description placeholder"),
                            "gacha_rarity": getattr(cls, "gacha_rarity", 5),
                            "char_type": str(getattr(cls, "char_type", "C")),
                            "banner_id": banner.id
                        })
                        break

        return featured_chars

    def _get_pity(self) -> int:
        with self.save.connection() as conn:
            cur = conn.execute(
                "SELECT value FROM options WHERE key = ?", ("gacha_pity",)
            )
            row = cur.fetchone()
            return int(row[0]) if row else 0

    def _set_pity(self, value: int) -> None:
        with self.save.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO options (key, value) VALUES (?, ?)",
                ("gacha_pity", str(value)),
            )

    def _get_items(self) -> dict[str, int]:
        with self.save.connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS upgrade_items (id TEXT PRIMARY KEY, count INTEGER NOT NULL)"
            )
            cur = conn.execute("SELECT id, count FROM upgrade_items")
            return {row[0]: int(row[1]) for row in cur.fetchall()}

    def _set_items(self, items: dict[str, int]) -> None:
        with self.save.connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS upgrade_items (id TEXT PRIMARY KEY, count INTEGER NOT NULL)"
            )
            for key, value in items.items():
                conn.execute(
                    "INSERT OR REPLACE INTO upgrade_items (id, count) VALUES (?, ?)",
                    (key, int(value)),
                )
            conn.execute("DELETE FROM upgrade_items WHERE count <= 0")

    def _get_auto_craft(self) -> bool:
        return True

    def _auto_craft(self, items: dict[str, int]) -> None:
        """Convert excess upgrade items into higher tiers.

        Crafting never creates items above 4★. Any surplus 4★ items remain at
        that tier so drop rate bonuses cannot raise the star level beyond the
        intended cap.
        """

        for element in ELEMENTS:
            for star in range(1, 4):
                lower = f"{element}_{star}"
                higher = f"{element}_{star + 1}"
                while items.get(lower, 0) >= 125:
                    items[lower] -= 125
                    items[higher] = items.get(higher, 0) + 1

        for key in [k for k, v in items.items() if v == 0]:
            del items[key]

    def craft(self) -> dict[str, int]:
        items = self._get_items()
        self._auto_craft(items)
        self._set_items(items)
        return items

    def _add_character(self, cid: str) -> int:
        with self.save.connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO owned_players (id) VALUES (?)",
                (cid,),
            )
            cur = conn.execute(
                "SELECT stacks FROM player_stacks WHERE id = ?", (cid,)
            )
            row = cur.fetchone()
            stacks = int(row[0]) + 1 if row else 1
            conn.execute(
                "INSERT OR REPLACE INTO player_stacks (id, stacks) VALUES (?, ?)",
                (cid, stacks),
            )
        return stacks

    def _get_owned(self) -> set[str]:
        with self.save.connection() as conn:
            cur = conn.execute("SELECT id FROM owned_players")
            return {row[0] for row in cur.fetchall()}

    def _rarity_weights(self, pity: int) -> list[float]:
        factor = min(pity, 180) / 180
        return [
            0.10 * (1 - factor),
            0.50 - 0.20 * factor,
            0.30 + 0.20 * factor,
            0.10 + 0.10 * factor,
        ]

    def pull(self, count: int, banner_id: str = "standard") -> list[PullResult]:
        if count not in (1, 5, 10):
            raise ValueError("invalid pull count")

        banner = self.get_active_banner(banner_id)
        if not banner:
            raise ValueError("banner not available")

        results: list[PullResult] = []
        pity = self._get_pity()
        items = self._get_items()
        if items.get("ticket", 0) < count:
            raise PermissionError("insufficient tickets")
        items["ticket"] = items.get("ticket", 0) - count
        owned = self._get_owned()

        for _ in range(count):
            if random.random() < 0.0001:
                # 6★ character pull
                if banner.banner_type == "custom" and banner.featured_character and banner.featured_character in SIX_STAR:
                    # Featured 6★ character has higher chance
                    if random.random() < 0.5:
                        cid = banner.featured_character
                    else:
                        pool = [c for c in SIX_STAR if c not in owned and c != banner.featured_character]
                        cid = random.choice(pool or SIX_STAR)
                else:
                    pool = [c for c in SIX_STAR if c not in owned]
                    cid = random.choice(pool or SIX_STAR)
                stacks = self._add_character(cid)
                owned.add(cid)
                results.append(PullResult("character", cid, 6, stacks))
                pity = 0
                continue

            pity_chance = 0.00001 + pity * ((0.05 - 0.00001) / 159)
            if pity >= 179 or random.random() < pity_chance:
                # 5★ character pull
                if banner.banner_type == "custom" and banner.featured_character and banner.featured_character in FIVE_STAR:
                    # Featured 5★ character has 50% chance
                    if random.random() < 0.5:
                        cid = banner.featured_character
                    else:
                        pool = [c for c in FIVE_STAR if c not in owned and c != banner.featured_character]
                        cid = random.choice(pool or FIVE_STAR)
                else:
                    pool = [c for c in FIVE_STAR if c not in owned]
                    cid = random.choice(pool or FIVE_STAR)
                stacks = self._add_character(cid)
                owned.add(cid)
                results.append(PullResult("character", cid, 5, stacks))
                pity = 0
            else:
                weights = self._rarity_weights(pity)
                roll = random.random()
                threshold = 0.0
                rarity = 1
                for idx, weight in enumerate(weights, start=1):
                    threshold += weight
                    if roll < threshold:
                        rarity = idx
                        break
                element = random.choice(ELEMENTS)
                key = f"{element}_{rarity}"
                items[key] = items.get(key, 0) + 1
                self._auto_craft(items)
                results.append(PullResult("item", key, rarity))
                pity += 1
        self._set_pity(pity)
        self._set_items(items)
        return results

    def get_state(self) -> dict[str, Any]:
        pity = self._get_pity()
        items = self._get_items()
        with self.save.connection() as conn:
            cur = conn.execute(
                "SELECT p.id, COALESCE(s.stacks, 0) FROM owned_players p LEFT JOIN player_stacks s ON p.id = s.id"
            )
            players = [
                {"id": row[0], "stacks": row[1]} for row in cur.fetchall()
            ]

        banners = self.get_available_banners()
        featured_characters = self.get_featured_characters()

        return {
            "pity": pity,
            "items": items,
            "players": players,
            "banners": [{"id": b.id, "name": b.name, "banner_type": b.banner_type, "featured_character": b.featured_character} for b in banners],
            "featured_characters": featured_characters,
        }
