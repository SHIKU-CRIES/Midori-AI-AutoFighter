import logging

from dataclasses import dataclass
from dataclasses import field

from autofighter.party import Party


log = logging.getLogger(__name__)


@dataclass
class RelicBase:
    plugin_type = "relic"

    id: str = ""
    name: str = ""
    stars: int = 1
    effects: dict[str, float] = field(default_factory=dict)
    about: str = ""

    def apply(self, party: Party) -> None:
        log.info("Applying relic %s to party", self.id)
        for member in party.members:
            log.debug("Applying relic to %s", getattr(member, "id", "member"))
            for attr, pct in self.effects.items():
                value = getattr(member, attr, None)
                if value is None:
                    continue
                new_value = type(value)(value * (1 + pct))
                setattr(member, attr, new_value)
                log.debug(
                    "Updated %s %s to %s",
                    getattr(member, "id", "member"),
                    attr,
                    new_value,
                )

    def describe(self, stacks: int) -> str:
        return self.about
