from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.stats import Stats


@dataclass
class Aftertaste:
    plugin_type = "effect"
    id = "aftertaste"

    hits: int = 1
    base_pot: int = 25
    rng: random.Random = field(default_factory=random.Random)

    def rolls(self) -> list[int]:
        return [int(self.base_pot * self.rng.uniform(0.1, 1.5)) for _ in range(self.hits)]

    async def apply(self, attacker: Stats, target: Stats) -> list[int]:
        results: list[int] = []
        for amount in self.rolls():
            dmg = await target.apply_damage(amount, attacker)
            results.append(dmg)
        return results
