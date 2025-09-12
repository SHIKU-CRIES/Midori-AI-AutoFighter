from autofighter.action_queue import GAUGE_START
from autofighter.action_queue import ActionQueue
from autofighter.stats import Stats


def test_speed_ordering_and_reset():
    a = Stats()
    a.id = "a"
    a.spd = 200  # base AV 50
    b = Stats()
    b.id = "b"
    b.spd = 100  # base AV 100
    q = ActionQueue([a, b])

    first = q.next_actor()
    assert first is a
    assert a.action_value == a.base_action_value
    assert b.action_value == b.base_action_value - a.base_action_value

    second = q.next_actor()
    assert second is b
    assert b.action_value == b.base_action_value
    assert a.action_value == 0

    snap = q.snapshot()
    assert [e["id"] for e in snap] == ["a", "b"]
    assert all(e["action_gauge"] == GAUGE_START for e in snap)


def test_bonus_turn():
    a = Stats()
    a.id = "a"
    a.spd = 200
    b = Stats()
    b.id = "b"
    b.spd = 100
    q = ActionQueue([a, b])

    first = q.next_actor()
    q.grant_extra_turn(first)

    snap = q.snapshot()
    assert snap[0]["id"] == first.id
    assert snap[0]["bonus"] is True

    second = q.next_actor()
    assert second is first

    third = q.next_actor()
    assert third is b

    snap = q.snapshot()
    assert all("bonus" not in e for e in snap)
