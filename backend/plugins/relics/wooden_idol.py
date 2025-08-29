from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.players._base import PlayerBase
from plugins.relics._base import RelicBase


@dataclass
class WoodenIdol(RelicBase):
    """+3% Effect Res; resisting a debuff grants +1% Effect Res next turn."""

    id: str = "wooden_idol"
    name: str = "Wooden Idol"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"effect_resistance": 0.03})
    about: str = "+3% Effect Res; resisting a debuff grants +1% Effect Res next turn."

    def apply(self, party) -> None:
        super().apply(party)

        pending: dict[int, float] = {}
        active: dict[int, tuple[PlayerBase, float]] = {}

        def _resisted(member) -> None:
            if member not in party.members:
                return
            pid = id(member)
            bonus = 0.01 * party.relics.count(self.id)
            pending[pid] = pending.get(pid, 0) + bonus
            
            # Track debuff resistance
            BUS.emit("relic_effect", "wooden_idol", member, "debuff_resisted", int(bonus * 100), {
                "ally": getattr(member, 'id', str(member)),
                "resistance_bonus_next_turn": bonus * 100,
                "total_pending_bonus": pending[pid] * 100,
                "stacks": party.relics.count(self.id)
            })

        def _turn_start() -> None:
            applied_count = 0
            for pid, bonus in list(pending.items()):
                member = next((m for m in party.members if id(m) == pid), None)
                if member is None:
                    continue
                member.effect_resistance += bonus
                active[pid] = (member, bonus)
                applied_count += 1
                
                # Track resistance buff application
                BUS.emit("relic_effect", "wooden_idol", member, "resistance_buff_applied", int(bonus * 100), {
                    "ally": getattr(member, 'id', str(member)),
                    "resistance_bonus": bonus * 100,
                    "new_total_resistance": member.effect_resistance * 100,
                    "duration_turns": 1
                })
            
            pending.clear()

        def _turn_end() -> None:
            for pid, (member, bonus) in list(active.items()):
                member.effect_resistance -= bonus
            active.clear()

        BUS.subscribe("debuff_resisted", _resisted)
        BUS.subscribe("turn_start", lambda *_: _turn_start())
        BUS.subscribe("turn_end", lambda *_: _turn_end())

    def describe(self, stacks: int) -> str:
        if stacks == 1:
            return "+3% Effect Res; resisting a debuff grants +1% Effect Res next turn."
        else:
            # Calculate actual multiplicative bonus: (1.03)^stacks - 1
            multiplier = (1.03 ** stacks) - 1
            total_res_pct = round(multiplier * 100)
            return (
                f"+{total_res_pct}% Effect Res ({stacks} stacks, multiplicative); resisting a debuff grants +1% Effect Res next turn."
            )
