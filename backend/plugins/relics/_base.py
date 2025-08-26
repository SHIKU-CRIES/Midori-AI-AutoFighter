from dataclasses import dataclass
from dataclasses import field
import logging

from autofighter.effects import EffectManager
from autofighter.effects import create_stat_buff
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
        mods = []
        for member in party.members:
            log.debug("Applying relic to %s", getattr(member, "id", "member"))
            mgr = getattr(member, "effect_manager", None)
            if mgr is None:
                mgr = EffectManager(member)
                member.effect_manager = mgr
            changes = {f"{attr}_mult": 1 + pct for attr, pct in self.effects.items()}
            if not changes:
                continue
            mod = create_stat_buff(member, name=self.id, turns=9999, **changes)
            mgr.add_modifier(mod)
            mods.append(mod)
        self._mods = mods

    def remove(self) -> None:
        for mod in getattr(self, "_mods", []):
            mod.remove()
        self._mods = []

    def describe(self, stacks: int) -> str:
        return self.about
