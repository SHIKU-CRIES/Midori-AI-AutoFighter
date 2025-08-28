import asyncio
from dataclasses import dataclass
from dataclasses import field
import logging

from autofighter.effects import EffectManager
from autofighter.effects import create_stat_buff
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

    async def apply(self, party: Party) -> None:
        log.info("Applying card %s to party", self.id)
        for member in party.members:
            log.debug("Applying effects to %s", getattr(member, "id", "member"))
            mgr = getattr(member, "effect_manager", None)
            if mgr is None:
                mgr = EffectManager(member)
                member.effect_manager = mgr
            for attr, pct in self.effects.items():
                changes = {f"{attr}_mult": 1 + pct}
                mod = create_stat_buff(
                    member, name=f"{self.id}_{attr}", turns=9999, **changes
                )
                mgr.add_modifier(mod)
                if attr == "max_hp":
                    heal = int(getattr(member, "hp", 0) * pct)
                    try:
                        asyncio.get_running_loop()
                    except RuntimeError:
                        await member.apply_healing(heal)
                    else:
                        asyncio.create_task(member.apply_healing(heal))
                    log.debug(
                        "Updated %s max_hp and healed %s",
                        getattr(member, "id", "member"),
                        heal,
                    )
                else:
                    log.debug(
                        "Updated %s %s via stat modifier",
                        getattr(member, "id", "member"),
                        attr,
                    )
