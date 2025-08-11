from __future__ import annotations

import json

from typing import Any
from pathlib import Path
from typing import get_origin
from dataclasses import fields
from dataclasses import MISSING
from typing import get_type_hints

from autofighter.saves import SaveManager
from autofighter.stats import Stats

DB_PATH = Path("save.db")
SETTINGS_PATH = Path("settings.json")
DEFAULT_SETTINGS: dict[str, Any] = {
    "sfx_volume": 0.5,
    "music_volume": 0.5,
    "stat_refresh_rate": 5,
    "pause_on_stats": True,
}


def _merge_stats(data: dict[str, Any]) -> Stats:
    """Return a ``Stats`` instance, filling missing fields with defaults."""
    defaults: dict[str, Any] = {}
    hints = get_type_hints(Stats)
    for field in fields(Stats):
        hint = hints.get(field.name, field.type)
        if field.default is not MISSING:
            defaults[field.name] = field.default
        elif field.default_factory is not MISSING:  # type: ignore[attr-defined]
            defaults[field.name] = field.default_factory()  # type: ignore[misc]
        else:
            origin = get_origin(hint)
            if hint in (int, float):
                defaults[field.name] = 0
            elif hint is bool:
                defaults[field.name] = False
            elif origin is list:
                defaults[field.name] = []
            else:
                defaults[field.name] = None
    defaults.update(data)
    return Stats(**defaults)


def load_settings(path: Path | None = None) -> dict[str, Any]:
    path = path or SETTINGS_PATH
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return {**DEFAULT_SETTINGS, **data}
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict[str, Any], path: Path | None = None) -> None:
    path = path or SETTINGS_PATH
    path.write_text(json.dumps(settings))


def load_run(source: Path | str, password: str = "", path: Path = DB_PATH) -> Stats | None:
    if isinstance(source, Path):
        if not source.exists():
            return None
        try:
            data = json.loads(source.read_text())
            stats_data = data.get("stats", {})
            return _merge_stats(stats_data)
        except Exception:
            return None
    with SaveManager(path, password) as sm:
        data = sm.fetch_run(source)
    if not data:
        return None
    stats_data = data.get("stats", {})
    return _merge_stats(stats_data)


def save_run(run_id: str, stats: Stats, password: str = "", path: Path = DB_PATH) -> None:
    payload = {"stats": stats.__dict__}
    with SaveManager(path, password) as sm:
        sm.queue_run(run_id, payload)
        sm.commit()


def save_player(
    body: str,
    hair: str,
    hair_color: str,
    accessory: str,
    stats: Stats,
    inventory: dict[str, int],
    password: str = "",
    path: Path = DB_PATH,
    player_id: str = "player",
) -> None:
    data: dict[str, Any] = {
        "body": body,
        "hair": hair,
        "hair_color": hair_color,
        "accessory": accessory,
        "stats": stats.__dict__,
        "inventory": inventory,
    }
    with SaveManager(path, password) as sm:
        existing = sm.fetch_player(player_id) or {}
        if "roster" in existing:
            data["roster"] = existing["roster"]
        sm.queue_player(player_id, data)
        sm.commit()


def load_player(
    password: str = "",
    path: Path = DB_PATH,
    player_id: str = "player",
) -> tuple[str, str, str, str, Stats, dict[str, int]] | None:
    with SaveManager(path, password) as sm:
        data = sm.fetch_player(player_id)
    if not data:
        return None
    stats_data = data.get("stats", {})
    stats = _merge_stats(stats_data)
    return (
        data.get("body", "Athletic"),
        data.get("hair", "Short"),
        data.get("hair_color", "Black"),
        data.get("accessory", "None"),
        stats,
        data.get("inventory", {}),
    )


def save_roster(
    roster: list[str],
    password: str = "",
    path: Path = DB_PATH,
    player_id: str = "player",
) -> None:
    with SaveManager(path, password) as sm:
        data = sm.fetch_player(player_id) or {}
        data["roster"] = roster
        sm.queue_player(player_id, data)
        sm.commit()


def load_roster(
    password: str = "",
    path: Path = DB_PATH,
    player_id: str = "player",
) -> list[str]:
    with SaveManager(path, password) as sm:
        data = sm.fetch_player(player_id)
    if not data:
        return []
    roster = data.get("roster", [])
    return [str(c) for c in roster]
