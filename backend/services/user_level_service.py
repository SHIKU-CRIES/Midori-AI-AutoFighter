from __future__ import annotations


def user_exp_to_level(level: int) -> int:
    base = 100
    return int(base * (1.05 ** (level - 1)))


def get_user_state() -> dict[str, int]:
    from game import get_save_manager

    with get_save_manager().connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
        )
        row = conn.execute(
            "SELECT value FROM options WHERE key = ?", ("user_level",)
        ).fetchone()
        try:
            level = int(row[0]) if row else 1
        except (TypeError, ValueError):
            level = 1
        row = conn.execute(
            "SELECT value FROM options WHERE key = ?", ("user_exp",)
        ).fetchone()
        try:
            exp = int(row[0]) if row else 0
        except (TypeError, ValueError):
            exp = 0
    next_level_exp = user_exp_to_level(level)
    return {"level": level, "exp": exp, "next_level_exp": next_level_exp}


def get_user_level() -> int:
    return get_user_state()["level"]


def gain_user_exp(amount: int) -> dict[str, int]:
    if amount <= 0:
        return get_user_state()
    state = get_user_state()
    exp = state["exp"] + amount
    level = state["level"]
    next_exp = user_exp_to_level(level)
    while exp >= next_exp:
        exp -= next_exp
        level += 1
        next_exp = user_exp_to_level(level)
    from game import get_save_manager

    with get_save_manager().connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO options (key, value) VALUES (?, ?)",
            ("user_level", str(level)),
        )
        conn.execute(
            "INSERT OR REPLACE INTO options (key, value) VALUES (?, ?)",
            ("user_exp", str(exp)),
        )
    return {"level": level, "exp": exp, "next_level_exp": next_exp}
