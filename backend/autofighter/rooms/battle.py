from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from collections.abc import Callable
import copy
from dataclasses import dataclass
import logging
import random
import time
from typing import Any

from autofighter.cards import apply_cards
from autofighter.cards import card_choices
from autofighter.effects import EffectManager
from autofighter.effects import StatModifier
from autofighter.effects import create_stat_buff
from autofighter.relics import apply_relics
from autofighter.relics import relic_choices
from plugins.damage_types import ALL_DAMAGE_TYPES

from ..party import Party
from ..passives import PassiveRegistry
from ..stats import BUS
from ..stats import Stats
from ..stats import set_enrage_percent
from . import Room
from .utils import _build_foes
from .utils import _scale_stats
from .utils import _serialize

log = logging.getLogger(__name__)

ENRAGE_TURNS_NORMAL = 100
ENRAGE_TURNS_BOSS = 500

ELEMENTS = [e.lower() for e in ALL_DAMAGE_TYPES]


def _pick_card_stars(room: Room) -> int:
    """Determine the star rank for card rewards."""
    roll = random.random()
    if isinstance(room, BossRoom):
        if roll < 0.60:
            return 3
        if roll < 0.85:
            return 4
        return 5
    if isinstance(room, BattleRoom) and room.strength > 1.0:
        if roll < 0.40:
            return 1
        if roll < 0.70:
            return 2
        if roll < 0.7015:
            return 3
        if roll < 0.7025:
            return 4
        return 5
    return 1 if roll < 0.80 else 2


def _roll_relic_drop(room: Room, rdr: float) -> bool:
    """Check whether a relic drops based on room type and RDR."""
    roll = random.random()
    base = 0.5 if isinstance(room, BossRoom) else 0.1
    return roll < min(base * rdr, 1.0)


def _pick_item_stars(room: Room) -> int:
    """Select upgrade item star rank based on room difficulty."""
    node = room.node
    if node.room_type == "battle-boss-floor":
        low, high = 3, 4
    elif isinstance(room, BossRoom) or getattr(room, "strength", 1.0) > 1.0:
        low, high = 1, 3
    else:
        low, high = 1, 2
    base = low + (node.floor - 1) // 20 + (node.loop - 1) + node.pressure // 10
    return min(base, high)


def _calc_gold(room: Room, rdr: float) -> int:
    """Calculate gold reward for the room."""
    node = room.node
    if node.room_type == "battle-boss-floor":
        base = 200
        mult = random.uniform(2.05, 4.25)
    elif isinstance(room, BossRoom) or getattr(room, "strength", 1.0) > 1.0:
        base = 20
        mult = random.uniform(1.53, 2.25)
    else:
        base = 5
        mult = random.uniform(1.01, 1.25)
    return int(base * node.loop * mult * rdr)


def _pick_relic_stars(room: Room) -> int:
    roll = random.random()
    if isinstance(room, BossRoom):
        if roll < 0.6:
            return 3
        if roll < 0.9:
            return 4
        return 5
    if roll < 0.7:
        return 1
    if roll < 0.9:
        return 2
    return 3


def _apply_rdr_to_stars(stars: int, rdr: float) -> int:
    """Chance to upgrade stars with extreme `rdr` values."""
    for threshold in (10.0, 10000.0):
        if stars >= 5 or rdr < threshold:
            break
        chance = min(rdr / (threshold * 10.0), 0.99)
        if random.random() < chance:
            stars += 1
        else:
            break
    return stars


@dataclass
class BattleRoom(Room):
    """Standard battle room where the party fights a group of foes."""

    strength: float = 1.0

    async def resolve(
        self,
        party: Party,
        data: dict[str, Any],
        progress: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
        foe: Stats | list[Stats] | None = None,
    ) -> dict[str, Any]:
        registry = PassiveRegistry()
        start_gold = party.gold
        if foe is None:
            foes = _build_foes(self.node, party)
        else:
            foes = foe if isinstance(foe, list) else [foe]
        for f in foes:
            _scale_stats(f, self.node, self.strength)
        foe = foes[0]
        combat_party = Party(
            members=[copy.deepcopy(m) for m in party.members],
            gold=party.gold,
            relics=party.relics,
            cards=party.cards,
            rdr=party.rdr,
        )
        apply_cards(combat_party)
        apply_relics(combat_party)
        party.rdr = combat_party.rdr

        foe_effects = []
        for f in foes:
            mgr = EffectManager(f)
            f.effect_manager = mgr
            foe_effects.append(mgr)
        enrage_mods: list[StatModifier | None] = [None for _ in foes]

        party_effects = []
        for member in combat_party.members:
            mgr = EffectManager(member)
            member.effect_manager = mgr
            party_effects.append(mgr)

        for f in foes:
            BUS.emit("battle_start", f)
            await registry.trigger("battle_start", f)
        log.info(
            "Battle start: %s vs %s",
            [f.id for f in foes],
            [m.id for m in combat_party.members],
        )
        for member_effect, member in zip(party_effects, combat_party.members, strict=False):
            BUS.emit("battle_start", member)
            await registry.trigger("battle_start", member)

        enrage_active = False
        enrage_stacks = 0
        enrage_bleed_applies = 0
        # Ensure enrage percent starts at 0 for this battle
        set_enrage_percent(0.0)
        threshold = ENRAGE_TURNS_BOSS if isinstance(self, BossRoom) else ENRAGE_TURNS_NORMAL
        exp_reward = 0
        turn = 0
        if progress is not None:
            await progress(
                {
                    "result": "battle",
                    "party": [_serialize(m) for m in combat_party.members],
                    "foes": [_serialize(f) for f in foes],
                    "enrage": {"active": False, "stacks": 0},
                    "rdr": party.rdr,
                }
            )
        while any(f.hp > 0 for f in foes) and any(
            m.hp > 0 for m in combat_party.members
        ):
            for member_effect, member in zip(party_effects, combat_party.members, strict=False):
                if member.hp <= 0:
                    continue
                turn += 1
                if turn > threshold:
                    if not enrage_active:
                        enrage_active = True
                        for f in foes:
                            f.passives.append("Enraged")
                        log.info("Enrage activated")
                    new_stacks = turn - threshold
                    # Each enrage stack adds +1% damage taken and -1% healing dealt globally
                    set_enrage_percent(0.01 * max(new_stacks, 0))
                    mult = 1 + 0.4 * new_stacks
                    for i, (f, mgr) in enumerate(zip(foes, foe_effects, strict=False)):
                        if enrage_mods[i] is not None:
                            enrage_mods[i].remove()
                            try:
                                mgr.mods.remove(enrage_mods[i])
                                if enrage_mods[i].id in f.mods:
                                    f.mods.remove(enrage_mods[i].id)
                            except ValueError:
                                pass
                        mod = create_stat_buff(f, name="enrage_atk", atk_mult=mult, turns=9999)
                        mgr.add_modifier(mod)
                        enrage_mods[i] = mod
                    enrage_stacks = new_stacks
                    if turn > 1000:
                        turns_in_enrage = max(enrage_stacks, 0)
                        extra_damage = 100 * turns_in_enrage
                        for m in combat_party.members:
                            if m.hp > 0 and extra_damage > 0:
                                await m.apply_damage(extra_damage)
                        for f in foes:
                            if f.hp > 0 and extra_damage > 0:
                                await f.apply_damage(extra_damage)
                else:
                    # Not enraged yet; ensure percent is zero
                    set_enrage_percent(0.0)
                turn_start = time.perf_counter()
                await registry.trigger("turn_start", member)
                log.debug("%s turn start", member.id)
                await member.maybe_regain(turn)
                # If all foes died earlier in this round, stop taking actions
                if not any(f.hp > 0 for f in foes):
                    break
                alive_foe_idxs = [i for i, f in enumerate(foes) if f.hp > 0]
                if not alive_foe_idxs:
                    break
                tgt_idx = random.choice(alive_foe_idxs)
                tgt_foe = foes[tgt_idx]
                tgt_mgr = foe_effects[tgt_idx]
                dt = getattr(member, "damage_type", None)
                await member_effect.tick(tgt_mgr)
                if member.hp <= 0:
                    await registry.trigger("turn_end", member)
                    elapsed = time.perf_counter() - turn_start
                    if elapsed < 0.5:
                        await asyncio.sleep(0.5 - elapsed)
                    continue
                proceed = await member_effect.on_action()
                if proceed is None:
                    proceed = True
                if proceed and hasattr(dt, "on_action"):
                    res = await dt.on_action(
                        member,
                        combat_party.members,
                        foes,
                    )
                    proceed = True if res is None else bool(res)
                if not proceed:
                    await registry.trigger("turn_end", member)
                    if progress is not None:
                        await progress(
                            {
                                "result": "battle",
                                "party": [_serialize(m) for m in combat_party.members],
                                "foes": [_serialize(f) for f in foes],
                                "enrage": {
                                    "active": enrage_active,
                                    "stacks": enrage_stacks,
                                },
                                "rdr": party.rdr,
                            }
                        )
                    elapsed = time.perf_counter() - turn_start
                    if elapsed < 0.5:
                        await asyncio.sleep(0.5 - elapsed)
                    continue
                dmg = await tgt_foe.apply_damage(member.atk, attacker=member)
                if dmg <= 0:
                    log.info("%s's attack was dodged by %s", member.id, tgt_foe.id)
                else:
                    log.info("%s hits %s for %s", member.id, tgt_foe.id, dmg)
                tgt_mgr.maybe_inflict_dot(member, dmg)
                if getattr(member.damage_type, "id", "").lower() == "wind":
                    for extra_idx, extra_foe in enumerate(foes):
                        if extra_idx == tgt_idx or extra_foe.hp <= 0:
                            continue
                        extra_dmg = await extra_foe.apply_damage(
                            member.atk, attacker=member
                        )
                        if extra_dmg <= 0:
                            log.info(
                                "%s's attack was dodged by %s",
                                member.id,
                                extra_foe.id,
                            )
                        else:
                            log.info(
                                "%s hits %s for %s",
                                member.id,
                                extra_foe.id,
                                extra_dmg,
                            )
                        foe_effects[extra_idx].maybe_inflict_dot(member, extra_dmg)
                        if extra_foe.hp <= 0:
                            exp_reward += extra_foe.level * 12 + 5 * self.node.index
                            try:
                                label = (
                                    getattr(extra_foe, "name", None)
                                    or getattr(extra_foe, "id", "")
                                ).lower()
                                if "slime" in label:
                                    for m in combat_party.members:
                                        m.exp_multiplier += 0.025
                                    for m in party.members:
                                        m.exp_multiplier += 0.025
                            except Exception:
                                pass
                # Keep prior enrage bleed: every 10 stacks since activation,
                # add increasing stacks of a %max HP DoT to both sides.
                if enrage_active:
                    turns_since_enrage = max(enrage_stacks, 0)
                    next_trigger = (enrage_bleed_applies + 1) * 10
                    if turns_since_enrage >= next_trigger:
                        stacks_to_add = 1 + enrage_bleed_applies
                        from autofighter.effects import DamageOverTime
                        for mgr in party_effects:
                            for _ in range(stacks_to_add):
                                dmg_per_tick = int(max(mgr.stats.max_hp, 1) * 0.05)
                                mgr.add_dot(
                                    DamageOverTime(
                                        "Enrage Bleed", dmg_per_tick, 10, "enrage_bleed"
                                    )
                                )
                        for mgr, foe_obj in zip(foe_effects, foes, strict=False):
                            for _ in range(stacks_to_add):
                                dmg_per_tick = int(max(foe_obj.max_hp, 1) * 0.05)
                                mgr.add_dot(
                                    DamageOverTime(
                                        "Enrage Bleed", dmg_per_tick, 10, "enrage_bleed"
                                    )
                                )
                        enrage_bleed_applies += 1
                await registry.trigger("turn_end", member)
                if progress is not None:
                    await progress(
                        {
                            "result": "battle",
                            "party": [_serialize(m) for m in combat_party.members],
                            "foes": [_serialize(f) for f in foes],
                            "enrage": {"active": enrage_active, "stacks": enrage_stacks},
                            "rdr": party.rdr,
                        }
                    )
                if tgt_foe.hp <= 0:
                    exp_reward += tgt_foe.level * 12 + 5 * self.node.index
                    try:
                        label = (getattr(tgt_foe, "name", None) or getattr(tgt_foe, "id", "")).lower()
                        if "slime" in label:
                            for m in combat_party.members:
                                m.exp_multiplier += 0.025
                            for m in party.members:
                                m.exp_multiplier += 0.025
                    except Exception:
                        pass
                    elapsed = time.perf_counter() - turn_start
                    if elapsed < 0.5:
                        await asyncio.sleep(0.5 - elapsed)
                    if all(f.hp <= 0 for f in foes):
                        break
                    continue
                # Foe actions are handled after all party members act
                # in a dedicated loop per living foe.
                # Continue to next party member.
                continue
            # End of party member loop
            # If party wiped during this round, stop taking actions
            if not any(m.hp > 0 for m in combat_party.members):
                break
            # Foes: each living foe takes exactly one action per round
            for foe_idx, acting_foe in enumerate(foes):
                if acting_foe.hp <= 0:
                    continue
                alive_targets = [
                    (idx, m)
                    for idx, m in enumerate(combat_party.members)
                    if m.hp > 0
                ]
                if not alive_targets:
                    break
                pidx, target = random.choices(
                    alive_targets,
                    weights=[m.defense * m.mitigation for _, m in alive_targets],
                )[0]
                target_effect = party_effects[pidx]
                foe_mgr = foe_effects[foe_idx]
                await registry.trigger("turn_start", acting_foe)
                log.debug("%s turn start targeting %s", acting_foe.id, target.id)
                await acting_foe.maybe_regain(turn)
                dt = getattr(acting_foe, "damage_type", None)
                await foe_mgr.tick(target_effect)
                if acting_foe.hp <= 0:
                    await registry.trigger("turn_end", acting_foe)
                    continue
                proceed = await foe_mgr.on_action()
                if proceed is None:
                    proceed = True
                if proceed and hasattr(dt, "on_action"):
                    res = await dt.on_action(acting_foe, foes, combat_party.members)
                    proceed = True if res is None else bool(res)
                if not proceed:
                    await registry.trigger("turn_end", acting_foe)
                    elapsed = time.perf_counter() - turn_start
                    if elapsed < 0.5:
                        await asyncio.sleep(0.5 - elapsed)
                    continue
                dmg = await target.apply_damage(acting_foe.atk, attacker=acting_foe)
                if dmg <= 0:
                    log.info("%s's attack was dodged by %s", acting_foe.id, target.id)
                else:
                    log.info("%s hits %s for %s", acting_foe.id, target.id, dmg)
                target_effect.maybe_inflict_dot(acting_foe, dmg)
                await registry.trigger("turn_end", acting_foe)
                elapsed = time.perf_counter() - turn_start
                if elapsed < 0.5:
                    await asyncio.sleep(0.5 - elapsed)
        # Signal completion as soon as the loop ends to help UIs stop polling
        # immediately, even before rewards are fully computed.
        if progress is not None:
            try:
                await progress(
                    {
                        "result": "battle",
                        "party": [_serialize(m) for m in combat_party.members],
                        "foes": [_serialize(f) for f in foes],
                        "enrage": {"active": enrage_active, "stacks": enrage_stacks},
                        "rdr": party.rdr,
                        "ended": True,
                    }
                )
            except Exception:
                pass

        for mod in enrage_mods:
            if mod is not None:
                mod.remove()
        for member, mgr in zip(combat_party.members, party_effects, strict=False):
            await mgr.cleanup(member)
        for foe_obj, mgr in zip(foes, foe_effects, strict=False):
            await mgr.cleanup(foe_obj)
        # Reset enrage percent after battle ends to avoid leaking to other battles.
        try:
            set_enrage_percent(0.0)
        except Exception:
            pass
        party.members = combat_party.members
        party.gold = combat_party.gold
        party.relics = combat_party.relics
        party.cards = combat_party.cards
        # Award experience to all surviving party members on victory before
        # serializing party state so level/EXP changes are reflected in the
        # response and persisted by save_party.
        if any(m.hp > 0 for m in party.members) and exp_reward > 0:
            for member in party.members:
                try:
                    member.gain_exp(exp_reward)
                except Exception:
                    # Do not let EXP calculation break battle resolution
                    pass
        party_data = [_serialize(p) for p in party.members]
        foes_data = [_serialize(f) for f in foes]
        if all(m.hp <= 0 for m in combat_party.members):
            loot = {
                "gold": 0,
                "card_choices": [],
                "relic_choices": [],
                "items": [],
            }
            return {
                "result": "defeat",
                "party": party_data,
                "gold": party.gold,
                "relics": party.relics,
                "cards": party.cards,
                "card_choices": [],
                "relic_choices": [],
                "loot": loot,
                "foes": foes_data,
                "room_number": self.node.index,
                "exp_reward": exp_reward,
                "enrage": {"active": enrage_active, "stacks": enrage_stacks},
                "rdr": party.rdr,
            }
        # Pick a star rank and fetch up to 3 unique card options the party doesn't own
        card_star = _pick_card_stars(self)
        card_opts = card_choices(combat_party, card_star, count=3)
        choice_data = [
            {
                "id": c.id,
                "name": c.name,
                "stars": c.stars,
                "about": c.about,
            }
            for c in card_opts
        ]
        relic_opts = []
        if _roll_relic_drop(self, party.rdr):
            relic_star = _apply_rdr_to_stars(_pick_relic_stars(self), party.rdr)
            # Offer 3 relic choices when a relic drop occurs
            relic_opts = relic_choices(combat_party, relic_star, count=3)
        relic_choice_data = [
            {
                "id": r.id,
                "name": r.name,
                "stars": r.stars,
                "about": r.describe(party.relics.count(r.id) + 1),
                "stacks": party.relics.count(r.id),
            }
            for r in relic_opts
        ]
        gold_reward = _calc_gold(self, party.rdr)
        party.gold += gold_reward
        BUS.emit("gold_earned", gold_reward)
        item_base = 1 * party.rdr
        base_int = int(item_base)
        item_count = max(1, base_int)
        if random.random() < item_base - base_int:
            item_count += 1
        items = [
            {"id": random.choice(ELEMENTS), "stars": _pick_item_stars(self)}
            for _ in range(item_count)
        ]
        ticket_chance = 0.1 * party.rdr
        if random.random() < ticket_chance:
            items.append({"id": "ticket", "stars": 0})
        loot = {
            "gold": party.gold - start_gold,
            "card_choices": choice_data,
            "relic_choices": relic_choice_data,
            "items": items,
        }
        log.info(
            "Battle rewards: gold=%s cards=%s relics=%s items=%s",
            loot["gold"],
            [c["id"] for c in choice_data],
            [r["id"] for r in relic_choice_data],
            items,
        )
        return {
            "result": "boss" if self.strength > 1.0 else "battle",
            "party": party_data,
            "gold": party.gold,
            "relics": party.relics,
            "cards": party.cards,
            "card_choices": choice_data,
            "relic_choices": relic_choice_data,
            "loot": loot,
            "foes": foes_data,
            "room_number": self.node.index,
            "exp_reward": exp_reward,
            "enrage": {"active": enrage_active, "stacks": enrage_stacks},
            "rdr": party.rdr,
        }


from .boss import BossRoom  # noqa: E402  # imported for isinstance checks
