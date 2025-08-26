from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.relics._base import RelicBase
from autofighter.effects import create_stat_buff


@dataclass
class ShinyPebble(RelicBase):
    """Raises DEF and gives a mitigation burst on the first hit."""

    id: str = "shiny_pebble"
    name: str = "Shiny Pebble"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"defense": 0.03})
    about: str = (
        "Boosts DEF and grants extra mitigation the first time an ally is hit."
    )

    def apply(self, party) -> None:
        super().apply(party)

        state = getattr(party, "_shiny_pebble_state", None)
        if state is None:
            state = {"active": {}, "triggered": set()}
            party._shiny_pebble_state = state

            def _first_hit(target, attacker, amount) -> None:
                if target not in party.members or id(target) in state["triggered"]:
                    return
                state["triggered"].add(id(target))
                stacks = party.relics.count(self.id)
                mit_mult = (1 + 0.03 * stacks) ** stacks
                mod = create_stat_buff(
                    target,
                    name=f"{self.id}_{id(target)}",
                    mitigation=target.mitigation * (mit_mult - 1),
                    turns=1,
                )
                target.effect_manager.add_modifier(mod)
                state["active"][id(target)] = (target, mod)

            def _reset(*_) -> None:
                for key, (member, mod) in list(state["active"].items()):
                    mod.remove()
                    if mod in member.effect_manager.mods:
                        member.effect_manager.mods.remove(mod)
                    if mod.id in member.mods:
                        member.mods.remove(mod.id)
                    state["active"].pop(key, None)

            BUS.subscribe("damage_taken", _first_hit)
            BUS.subscribe("turn_start", _reset)

    def describe(self, stacks: int) -> str:
        defense = 3 * stacks
        mit = 3 * stacks
        return (
            f"+{defense}% DEF. The first time each ally is hit, they gain +{mit}% mitigation for one turn."
        )
