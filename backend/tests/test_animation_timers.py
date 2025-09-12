from autofighter.stats import Stats
from autofighter.stats import calc_animation_time


def test_animation_time_scaling():
    actor = Stats()
    actor.animation_duration = 0.5
    actor.animation_per_target = 0.25
    assert calc_animation_time(actor, 1) == 0.5
    assert calc_animation_time(actor, 3) == 1.0
