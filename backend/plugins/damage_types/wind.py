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
    # every living foe multiple times and temporarily increase the user's
    # effect hit rate so Gale Erosion applies more reliably. The number of hits
    # is derived dynamically (from actor.wind_ultimate_hits or actor.ultimate_hits)
    # to allow relics/cards to adjust it.

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

        # Determine dynamic hit count (allow cards/relics to override via attributes)
        # Scale down hits for performance with many enemies
        base_hits = int(getattr(actor, "wind_ultimate_hits", getattr(actor, "ultimate_hits", 25)) or 25)
        enemy_count = len([foe for foe in enemies if getattr(foe, "hp", 0) > 0])
        # Scale hits down when fighting many enemies to maintain performance
        # 1-4 enemies: full hits, 5-8 enemies: 80%, 9-12 enemies: 60%, 13+ enemies: 40%
        if enemy_count <= 4:
            hits = base_hits
        elif enemy_count <= 8:
            hits = max(1, int(base_hits * 0.8))
        elif enemy_count <= 12:
            hits = max(1, int(base_hits * 0.6))
        else:
            hits = max(1, int(base_hits * 0.4))
        hits = max(1, hits)

        # Strike each living enemy with a total budget equal to actor.atk distributed
        # across all hits and all targets. This keeps Wind ultimate AoE damage in line
        # with single-target ults while preserving multi-hit feel.
        base = int(getattr(actor, "atk", 0))
        base = max(1, base)

        living = [foe for foe in enemies if getattr(foe, "hp", 0) > 0]
        if not living:
            return True
        total_chunks = hits * len(living)
        per = base // total_chunks
        rem = base - per * total_chunks

        for foe in living:
            if getattr(foe, "hp", 0) <= 0:
                continue
            f_mgr = getattr(foe, "effect_manager", None)
            if f_mgr is None:
                f_mgr = EffectManager(foe)
                foe.effect_manager = f_mgr
            for i in range(hits):
                if getattr(foe, "hp", 0) <= 0:
                    break
                # Fair rounding across all chunks (targets x hits)
                add_one = 1 if rem > 0 else 0
                per_hit = per + add_one
                if rem > 0:
                    rem -= 1
                # Ensure a minimum of 1 damage per hit going into the resolver
                per_hit = max(1, int(per_hit))
                dmg = await foe.apply_damage(per_hit, attacker=actor, action_name="Wind Ultimate")
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
                # Only yield every few hits when there are many enemies to reduce overhead
                if i % max(1, hits // 10) == 0:
                    await asyncio.sleep(0)

        # Clean up the temporary buff immediately after the sequence
        try:
            eh_mod.remove()
        except Exception:
            pass
        return True
