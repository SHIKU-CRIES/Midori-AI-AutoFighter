from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.players._base import PlayerBase
from plugins.relics._base import RelicBase


@dataclass
class TravelersCharm(RelicBase):
    """When hit, gain +25% DEF and +10% mitigation next turn per stack."""

    id: str = "travelers_charm"
    name: str = "Traveler's Charm"
    stars: int = 4
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "When hit, gain +25% DEF and +10% mitigation next turn per stack."

    def apply(self, party) -> None:
        super().apply(party)

        pending: dict[int, tuple[int, int]] = {}
        active: dict[int, tuple[PlayerBase, object]] = {}

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
                mod = create_stat_buff(
                    member,
                    name=f"{self.id}_{pid}",
                    turns=1,
                    defense=bdef,
                    mitigation=bmit,
                )
                member.effect_manager.add_modifier(mod)
                active[pid] = (member, mod)
            pending.clear()

        def _turn_end() -> None:
            for pid, (member, mod) in list(active.items()):
                mod.remove()
                if mod in member.effect_manager.mods:
                    member.effect_manager.mods.remove(mod)
                if mod.id in member.mods:
                    member.mods.remove(mod.id)
            active.clear()

        BUS.subscribe("damage_taken", _hit)
        BUS.subscribe("turn_start", lambda *_: _turn_start())
        BUS.subscribe("turn_end", lambda *_: _turn_end())

    def describe(self, stacks: int) -> str:
        d = 25 * stacks
        m = 10 * stacks
        return f"When hit, gain +{d}% DEF and +{m}% mitigation next turn."
