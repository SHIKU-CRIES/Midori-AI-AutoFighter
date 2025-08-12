import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "event_bus", Path(__file__).resolve().parents[1] / "plugins" / "event_bus.py"
)
event_bus_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(event_bus_module)
EventBus = event_bus_module.EventBus


def test_event_bus_emit_and_unsubscribe():
    bus = EventBus()
    received = []

    def handler(value):
        received.append(value)

    bus.subscribe("test", handler)
    bus.emit("test", 1)
    assert received == [1]
    bus.unsubscribe("test", handler)
    bus.emit("test", 2)
    assert received == [1]
