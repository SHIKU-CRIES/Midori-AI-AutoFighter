from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.players._base import PlayerBase
from plugins.relics._base import RelicBase


@dataclass
class TravelersCharm(RelicBase):
    """When hit, gain +25% DEF and +10% mitigation next turn per stack."""

    id: str = "travelers_charm"
    name: str = "Traveler's Charm"
    stars: int = 4
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "When hit, gain +25% DEF and +10% mitigation next turn per stack."

    def apply(self, party) -> None:
        super().apply(party)

        pending: dict[int, tuple[float, float]] = {}
        active: dict[int, tuple[PlayerBase, object]] = {}

        def _hit(target, attacker, amount) -> None:
            if target not in party.members:
                return
            pid = id(target)
            stacks = party.relics.count(self.id)
            d_pct = 0.25 * stacks
            m_pct = 0.10 * stacks
            pd, pm = pending.get(pid, (0.0, 0.0))
            pending[pid] = (pd + d_pct, pm + m_pct)

            # Track hit reaction
            BUS.emit(
                "relic_effect",
                "travelers_charm",
                target,
                "hit_reaction",
                amount,
                {
                    "target": getattr(target, "id", str(target)),
                    "attacker": getattr(attacker, "id", str(attacker)),
                    "pending_defense_pct": d_pct * 100,
                    "pending_mitigation_pct": m_pct * 100,
                    "stacks": stacks,
                    "triggers_next_turn": True,
                },
            )

        def _turn_start() -> None:
            applied_count = 0
            for pid, (d_pct, m_pct) in list(pending.items()):
                member = next((m for m in party.members if id(m) == pid), None)
                if member is None:
                    continue
                mod = create_stat_buff(
                    member,
                    name=f"{self.id}_{pid}",
                    turns=1,
                    defense_mult=1 + d_pct,
                    mitigation_mult=1 + m_pct,
                )
                member.effect_manager.add_modifier(mod)
                active[pid] = (member, mod)
                applied_count += 1

                # Track buff application
                BUS.emit(
                    "relic_effect",
                    "travelers_charm",
                    member,
                    "defensive_buff_applied",
                    int((d_pct + m_pct) * 100),
                    {
                        "ally": getattr(member, "id", str(member)),
                        "defense_multiplier": 1 + d_pct,
                        "mitigation_multiplier": 1 + m_pct,
                        "defense_bonus_pct": d_pct * 100,
                        "mitigation_bonus_pct": m_pct * 100,
                        "duration_turns": 1,
                        "triggered_by": "previous_hits",
                    },
                )

            pending.clear()

        def _turn_end() -> None:
            for pid, (member, mod) in list(active.items()):
                mod.remove()
                if mod in member.effect_manager.mods:
                    member.effect_manager.mods.remove(mod)
                if mod.id in member.mods:
                    member.mods.remove(mod.id)
            active.clear()

        BUS.subscribe("damage_taken", _hit)
        BUS.subscribe("turn_start", lambda *_: _turn_start())
        BUS.subscribe("turn_end", lambda *_: _turn_end())

    def describe(self, stacks: int) -> str:
        d = 25 * stacks
        m = 10 * stacks
        return f"When hit, gain +{d}% DEF and +{m}% mitigation next turn."
