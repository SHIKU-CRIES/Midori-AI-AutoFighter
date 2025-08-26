from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.relics._base import RelicBase


@dataclass
class StellarCompass(RelicBase):
    """Critical hits grant permanent +1.5% ATK and gold rate."""

    id: str = "stellar_compass"
    name: str = "Stellar Compass"
    stars: int = 3
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "Critical hits grant permanent +1.5% ATK and gold rate."

    def apply(self, party) -> None:
        super().apply(party)

        state = getattr(party, "_stellar_compass_state", None)
        if state is None:
            state = {"gold": 0.0}
            party._stellar_compass_state = state

            def _crit(attacker, target, amount) -> None:
                if attacker not in party.members:
                    return
                copies = party.relics.count(self.id)
                mod = create_stat_buff(
                    attacker,
                    name=f"{self.id}_crit",
                    atk_mult=1.015 ** copies,
                    turns=9999,
                )
                attacker.effect_manager.add_modifier(mod)
                state["gold"] += 0.015 * copies

            def _gold(amount: int) -> None:
                if state["gold"] > 0:
                    party.gold += int(amount * state["gold"])

            BUS.subscribe("crit_hit", _crit)
            BUS.subscribe("gold_earned", _gold)

    def describe(self, stacks: int) -> str:
        bonus = 1.5 * stacks
        return (
            f"Critical hits grant permanent +{bonus:.1f}% ATK and gold gain."
        )
