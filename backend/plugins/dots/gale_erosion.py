from autofighter.effects import DamageOverTime


class GaleErosion(DamageOverTime):
    plugin_type = "dot"
    id = "gale_erosion"

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Gale Erosion", damage, turns, self.id)

    def tick(self, target, *_):
        # Reduce mitigation by 1 each tick, but never below 0.5 due to Wind erosion.
        try:
            current = float(getattr(target, "mitigation", 1.0))
        except Exception:
            current = 1.0
        # Clamp at 0.5 minimum for this effect
        target.mitigation = max(current - 1.0, 0.5)
        return super().tick(target)
