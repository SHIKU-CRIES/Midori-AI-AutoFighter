from dataclasses import dataclass
from dataclasses import field

from plugins.relics._base import RelicBase
from autofighter.stats import BUS
from plugins.players._base import PlayerBase


@dataclass
class TravelersCharm(RelicBase):
    """When hit, gain +25% DEF and +10% mitigation next turn per stack."""

    id: str = "travelers_charm"
    name: str = "Traveler's Charm"
    stars: int = 4
    effects: dict[str, float] = field(default_factory=dict)

    def apply(self, party) -> None:
        super().apply(party)

        pending: dict[int, tuple[int, int]] = {}
        active: dict[int, tuple[PlayerBase, int, int]] = {}

        def _hit(target, attacker, amount) -> None:
            if target not in party.members:
                return
            pid = id(target)
            bdef = int(target.defense * 0.25)
            bmit = 10
            pd, pm = pending.get(pid, (0, 0))
            pending[pid] = (pd + bdef, pm + bmit)

        def _turn_start() -> None:
            for pid, (bdef, bmit) in list(pending.items()):
                member = next((m for m in party.members if id(m) == pid), None)
                if member is None:
                    continue
                member.defense += bdef
                member.mitigation += bmit
                active[pid] = (member, bdef, bmit)
            pending.clear()

        def _turn_end() -> None:
            for pid, (member, bdef, bmit) in list(active.items()):
                member.defense -= bdef
                member.mitigation -= bmit
            active.clear()

        BUS.subscribe("damage_taken", _hit)
        BUS.subscribe("turn_start", lambda: _turn_start())
        BUS.subscribe("turn_end", lambda: _turn_end())
