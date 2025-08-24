from typing import TYPE_CHECKING
from dataclasses import dataclass

from autofighter.stats import BUS
from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase

if TYPE_CHECKING:
    from plugins.dots.shadow_siphon import ShadowSiphon
    from plugins.dots.abyssal_corruption import AbyssalCorruption


@dataclass
class Dark(DamageTypeBase):
    id: str = "Dark"
    weakness: str = "Light"
    color: tuple[int, int, int] = (145, 0, 145)

    _cleanup_registered: bool = False

    async def on_action(self, actor, allies, enemies) -> bool:
        from plugins.dots.shadow_siphon import ShadowSiphon

        for member in allies:
            mgr = getattr(member, "effect_manager", None)
            if mgr is not None:
                dmg = int(member.max_hp * 0.05)
                mgr.add_dot(ShadowSiphon(dmg))

        if not self._cleanup_registered:
            def _clear(_):
                from plugins.dots.shadow_siphon import ShadowSiphon

                for member in allies:
                    member.dots = [d for d in member.dots if d != ShadowSiphon.id]
                    mgr = getattr(member, "effect_manager", None)
                    if mgr is not None:
                        mgr.dots = [d for d in mgr.dots if getattr(d, "id", "") != ShadowSiphon.id]
                self._cleanup_registered = False

            BUS.subscribe("battle_end", _clear)
            self._cleanup_registered = True

        return True

    def on_party_dot_damage_taken(self, damage, attacker, target) -> float:
        """Grant a tiny scaling bonus when Dark DoTs tick on allies.

        If the ticking DoT comes from a Dark attacker and the target is
        currently affected by Shadow Siphon, increase the attacker's
        offensive and defensive stats by a factor proportional to the
        damage dealt as a fraction of the target's max HP.

        The incoming ``damage`` value is returned unchanged; only the
        attacker is adjusted.
        """

        try:
            # Preconditions: source must be Dark and the target must have Shadow Siphon.
            if getattr(attacker, "damage_type", None) is not self:
                return damage
            from plugins.dots.shadow_siphon import ShadowSiphon

            if ShadowSiphon.id not in getattr(target, "dots", []):
                return damage

            # Compute damage as a fraction of max HP (guard against div-by-zero).
            max_hp = max(float(getattr(target, "max_hp", 0) or 0.0), 1.0)
            percent_of_max = max(float(damage) / max_hp, 0.0)

            # 0.05 per 1.0 (i.e., +5% when DoT equals 100% of max HP).
            scale = 1.0 + percent_of_max * 0.05

            # Apply scale to common stats if present on attacker.
            if hasattr(attacker, "atk"):
                attacker.atk = int(attacker.atk * scale) + 1
            if hasattr(attacker, "defense"):
                attacker.defense = int(attacker.defense * scale)
        except Exception:
            # Intentionally swallow errors to avoid breaking combat flow.
            pass
        return damage

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        from plugins.dots.abyssal_corruption import AbyssalCorruption

        dot = AbyssalCorruption(int(damage * 0.4), 3)
        dot.source = source
        return dot
