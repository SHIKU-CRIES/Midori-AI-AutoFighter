from plugins.foes._base import FoeBase
from plugins.players._base import PlayerBase


def test_player_has_default_aggro_field():
    field = PlayerBase.__dataclass_fields__["aggro"]
    assert field.default == 0.1


def test_foe_has_default_aggro_field():
    field = FoeBase.__dataclass_fields__["aggro"]
    assert field.default == 0.1
