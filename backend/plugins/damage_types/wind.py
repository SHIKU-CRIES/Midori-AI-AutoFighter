import asyncio
from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from autofighter.effects import EffectManager
from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins import damage_effects
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Wind(DamageTypeBase):
    id: str = "Wind"
    weakness: str = "Lightning"
    color: tuple[int, int, int] = (0, 255, 0)

    # Previous implementation scattered DoTs after an ultimate by moving
    # existing effects. The new design: when Wind uses its ultimate, strike
    # every living foe 25 times and temporarily increase the user's
    # effect hit rate so Gale Erosion applies more reliably.

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return damage_effects.create_dot(self.id, damage, source)

    async def ultimate(self, actor, allies, enemies):
        # Consume ultimate; bail if not ready
        if not getattr(actor, "use_ultimate", lambda: False)():
            return False

        # Ensure the actor has an EffectManager so temporary buffs apply cleanly
        a_mgr = getattr(actor, "effect_manager", None)
        if a_mgr is None:
            a_mgr = EffectManager(actor)
            actor.effect_manager = a_mgr

        # Apply a short-lived boost to effect hit rate to increase Wind DoT odds
        eh_mod = create_stat_buff(
            actor,
            name="wind_ultimate_effect_hit",
            turns=1,
            effect_hit_rate_mult=1.5,
        )
        a_mgr.add_modifier(eh_mod)

        # Strike each living enemy 25 times
        for foe in enemies:
            if getattr(foe, "hp", 0) <= 0:
                continue
            f_mgr = getattr(foe, "effect_manager", None)
            if f_mgr is None:
                f_mgr = EffectManager(foe)
                foe.effect_manager = f_mgr
            for _ in range(25):
                if getattr(foe, "hp", 0) <= 0:
                    break
                dmg = await foe.apply_damage(getattr(actor, "atk", 0), attacker=actor, action_name="Wind Ultimate")
                # Emit hit event for logging/passives, mirroring battle loop behavior
                try:
                    await BUS.emit_async("hit_landed", actor, foe, dmg, "attack", "wind_ultimate")
                except Exception:
                    pass
                # Roll Gale Erosion on each hit based on (boosted) effect hit rate
                try:
                    f_mgr.maybe_inflict_dot(actor, dmg)
                except Exception:
                    pass
                # Yield briefly to keep event loop responsive during large hit counts
                await asyncio.sleep(0)

        # Clean up the temporary buff immediately after the sequence
        try:
            eh_mod.remove()
        except Exception:
            pass
        return True
