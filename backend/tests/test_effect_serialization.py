from autofighter.effects import DamageOverTime, EffectManager, HealingOverTime
from autofighter.rooms.utils import _serialize
from autofighter.stats import Stats


def test_serialize_effect_details():
    target = Stats()
    target.id = "t"
    mgr = EffectManager(target)
    target.effect_manager = mgr

    source = Stats()
    source.id = "s"
    mgr.add_dot(DamageOverTime("burn", 5, 2, "burn", source))
    mgr.add_dot(DamageOverTime("burn", 5, 1, "burn", source))
    mgr.add_hot(HealingOverTime("regen", 3, 1, "regen", source))

    target.passives = ["p1", "p1", "p2"]

    data = _serialize(target)

    assert data["dots"] == [
        {
            "id": "burn",
            "name": "burn",
            "damage": 5,
            "turns": 2,
            "source": "s",
            "stacks": 2,
        }
    ]
    assert data["hots"] == [
        {
            "id": "regen",
            "name": "regen",
            "healing": 3,
            "turns": 1,
            "source": "s",
            "stacks": 1,
        }
    ]
    assert any(p["id"] == "p1" and p["stacks"] == 2 for p in data["passives"])
    assert any(p["id"] == "p2" and p["stacks"] == 1 for p in data["passives"])
