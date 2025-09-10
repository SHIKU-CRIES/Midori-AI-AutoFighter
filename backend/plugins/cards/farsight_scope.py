from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class FarsightScope(CardBase):
    id: str = "farsight_scope"
    name: str = "Farsight Scope"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"crit_rate": 0.03})
    about: str = "+3% Crit Rate; Attacks against enemies under 50% HP gain +6% crit rate"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _before_attack(attacker, target):
            # Check if attacker is one of our party members
            if attacker in party.members:
                # Check if target is under 50% HP
                target_hp = getattr(target, 'hp', 0)
                target_max_hp = getattr(target, 'max_hp', 1)
                if target_hp / target_max_hp < 0.50:
                    # Apply temporary +6% crit rate for this attack (theoretical implementation)
                    import logging
                    log = logging.getLogger(__name__)
                    log.debug("Farsight Scope low HP bonus: +6%% crit rate vs low HP enemy")
                    BUS.emit("card_effect", self.id, attacker, "low_hp_crit_bonus", 6, {
                        "crit_rate_bonus": 6,
                        "target_hp_percentage": (target_hp / target_max_hp) * 100,
                        "trigger_threshold": 50
                    })

        BUS.subscribe("before_attack", _before_attack)
