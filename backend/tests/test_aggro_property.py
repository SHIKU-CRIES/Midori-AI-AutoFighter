import pytest

from autofighter.stats import Stats
from plugins.damage_types.generic import Generic
from plugins.foes._base import FoeBase
from plugins.players._base import PlayerBase


def test_base_stats_aggro_calculation():
    s = Stats(damage_type=Generic())
    assert s.aggro == pytest.approx(0.11, rel=1e-3)


def test_player_has_aggro_property():
    player = PlayerBase(damage_type=Generic())
    assert isinstance(player.aggro, float)


def test_foe_has_aggro_property():
    foe = FoeBase(damage_type=Generic())
    assert isinstance(foe.aggro, float)
