import logging

from dataclasses import dataclass
from dataclasses import field

from autofighter.party import Party


log = logging.getLogger(__name__)


@dataclass
class CardBase:
    plugin_type = "card"

    id: str = ""
    name: str = ""
    stars: int = 1
    effects: dict[str, float] = field(default_factory=dict)
    about: str = ""

    def __post_init__(self) -> None:
        if not self.about and self.effects:
            parts: list[str] = []
            for attr, pct in self.effects.items():
                sign = "+" if pct >= 0 else ""
                pretty = attr.replace("_", " ")
                parts.append(f"{sign}{pct * 100:.0f}% {pretty}")
            self.about = ", ".join(parts)

    def apply(self, party: Party) -> None:
        log.info("Applying card %s to party", self.id)
        for member in party.members:
            log.debug("Applying effects to %s", getattr(member, "id", "member"))
            for attr, pct in self.effects.items():
                if attr == "max_hp":
                    member.max_hp = type(member.max_hp)(member.max_hp * (1 + pct))
                    member.hp = type(member.hp)(member.hp * (1 + pct))
                    log.debug(
                        "Updated %s max_hp and hp", getattr(member, "id", "member")
                    )
                else:
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
