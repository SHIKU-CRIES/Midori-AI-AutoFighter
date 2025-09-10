from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class EnergizingTea(CardBase):
    id: str = "energizing_tea"
    name: str = "Energizing Tea"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"regain": 0.03})
    about: str = "+3% Regain; At battle start, gain +1 energy on the first turn"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        battle_started = False

        def _on_battle_start(target):
            nonlocal battle_started
            # Only trigger once per battle and only for party members
            if not battle_started and target in party.members:
                battle_started = True
                # Give +1 energy to all party members
                for member in party.members:
                    old_energy = getattr(member, 'energy', 0)
                    max_energy = getattr(member, 'max_energy', 100)
                    if hasattr(member, 'energy'):
                        member.energy = min(max_energy, old_energy + 1)
                        import logging
                        log = logging.getLogger(__name__)
                        log.debug("Energizing Tea bonus energy: +1 energy to %s", member.id)
                        BUS.emit("card_effect", self.id, member, "energy_bonus", 1, {
                            "energy_bonus": 1,
                            "trigger_event": "battle_start"
                        })

        BUS.subscribe("battle_start", _on_battle_start)

