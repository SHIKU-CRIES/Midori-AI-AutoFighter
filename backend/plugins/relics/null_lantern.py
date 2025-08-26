from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.relics._base import RelicBase
from autofighter.effects import create_stat_buff


@dataclass
class NullLantern(RelicBase):
    """Removes shops/rests and converts fights into pulls."""

    id: str = "null_lantern"
    name: str = "Null Lantern"
    stars: int = 4
    effects: dict[str, float] = field(default_factory=lambda: {})
    about: str = "Shops and rest rooms vanish; each fight grants extra pulls."

    def apply(self, party) -> None:
        """Disable shops/rests, buff foes, and award pull tokens."""
        super().apply(party)

        party.no_shops = True
        party.no_rests = True
        stacks = party.relics.count(self.id)
        state = {"cleared": 0}

        if not hasattr(party, "pull_tokens"):
            party.pull_tokens = 0

        def _battle_start(entity) -> None:
            from plugins.foes._base import FoeBase

            if isinstance(entity, FoeBase):
                mult = 1 + 1.5 * state["cleared"]
                mod = create_stat_buff(
                    entity,
                    name=f"{self.id}_foe_{state['cleared']}",
                    turns=9999,
                    atk_mult=mult,
                    defense_mult=mult,
                    max_hp_mult=mult,
                    hp_mult=mult,
                )
                entity.effect_manager.add_modifier(mod)

        def _battle_end(entity) -> None:
            from plugins.foes._base import FoeBase

            if isinstance(entity, FoeBase):
                state["cleared"] += 1
                party.pull_tokens += 1 + (stacks - 1)

        BUS.subscribe("battle_start", _battle_start)
        BUS.subscribe("battle_end", _battle_end)

    def describe(self, stacks: int) -> str:
        pulls = 1 + (stacks - 1)
        return (
            "Shops and rest rooms vanish. Foes grow stronger each fight; "
            f"each clear grants {pulls} pull{'s' if pulls != 1 else ''}."
        )
