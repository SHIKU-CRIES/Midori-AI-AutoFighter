import asyncio

from dataclasses import field
from dataclasses import dataclass

from autofighter.stats import BUS
from plugins.relics._base import RelicBase


@dataclass
class GreedEngine(RelicBase):
    """Lose HP each turn but gain extra gold and rare drops."""

    id: str = "greed_engine"
    name: str = "Greed Engine"
    stars: int = 3
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "Lose HP each turn but gain extra gold and rare drops."

    def apply(self, party) -> None:
        super().apply(party)

        stacks = party.relics.count(self.id)
        gold_bonus = 0.5 + 0.25 * (stacks - 1)
        hp_loss = 0.01 + 0.005 * (stacks - 1)
        rdr_bonus = 0.005 + 0.001 * (stacks - 1)

        state = getattr(party, "_greed_engine_state", None)
        if state is None:
            state = {"gold": gold_bonus, "loss": hp_loss, "rdr": rdr_bonus}
            party._greed_engine_state = state
            party.rdr += state["rdr"]

            def _gold(amount: int) -> None:
                party.gold += int(amount * state["gold"])

            def _drain() -> None:
                for member in party.members:
                    dmg = int(member.max_hp * state["loss"])
                    asyncio.create_task(member.apply_damage(dmg))

            BUS.subscribe("gold_earned", _gold)
            BUS.subscribe("turn_start", _drain)
        else:
            party.rdr -= state.get("rdr", 0)
            state["gold"] = gold_bonus
            state["loss"] = hp_loss
            state["rdr"] = rdr_bonus
            party.rdr += state["rdr"]

    def describe(self, stacks: int) -> str:
        gold = 50 + 25 * (stacks - 1)
        hp = 1 + 0.5 * (stacks - 1)
        rdr = 0.5 + 0.1 * (stacks - 1)
        return (
            f"Party loses {hp:.1f}% HP each turn, gains {gold:.0f}% more gold, "
            f"and increases rare drop rate by {rdr:.1f}%."
        )
