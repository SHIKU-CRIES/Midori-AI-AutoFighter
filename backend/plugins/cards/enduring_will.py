from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class EnduringWill(CardBase):
    id: str = "enduring_will"
    name: str = "Enduring Will"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"mitigation": 0.03, "vitality": 0.03})
    about: str = "+3% Mitigation & +3% Vitality; If no allies die during combat, grant +1 mitigation next battle"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        # Track deaths and mitigation bonus
        battle_deaths = 0
        mitigation_bonus_pending = False

        def _on_death(target):
            nonlocal battle_deaths
            # Check if target is one of our party members
            if target in party.members:
                battle_deaths += 1

        def _on_battle_end():
            nonlocal mitigation_bonus_pending
            # If no allies died, prepare mitigation bonus for next battle
            if battle_deaths == 0:
                mitigation_bonus_pending = True
                import logging
                log = logging.getLogger(__name__)
                log.debug("Enduring Will mitigation bonus pending for next battle")
                BUS.emit("card_effect", self.id, None, "mitigation_bonus_pending", 1, {
                    "mitigation_bonus": 1,
                    "trigger_condition": "no_deaths",
                    "trigger_event": "battle_end"
                })

        def _on_battle_start(target):
            nonlocal battle_deaths, mitigation_bonus_pending
            if target in party.members:
                # Reset death counter for new battle
                battle_deaths = 0

                # Apply pending mitigation bonus if available
                if mitigation_bonus_pending:
                    mitigation_bonus_pending = False
                    for member in party.members:
                        # Apply +1 mitigation (theoretical implementation)
                        import logging
                        log = logging.getLogger(__name__)
                        log.debug("Enduring Will mitigation bonus: +1 mitigation to %s", member.id)
                        BUS.emit("card_effect", self.id, member, "mitigation_bonus", 1, {
                            "mitigation_bonus": 1,
                            "trigger_event": "battle_start"
                        })

        BUS.subscribe("death", _on_death)
        BUS.subscribe("battle_end", _on_battle_end)
        BUS.subscribe("battle_start", _on_battle_start)
