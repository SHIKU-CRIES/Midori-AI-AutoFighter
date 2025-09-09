# Event Bus Wrapper

Provides a simple publish/subscribe bus so plugins can communicate without engine-specific dependencies.

## Usage
- `subscribe(event: str, callback: Callable)` – register a function to run when an event is emitted.
- `unsubscribe(event: str, callback: Callable)` – stop receiving a previously subscribed event.
- `emit(event: str, *args)` – broadcast an event with optional arguments.

Subscriber errors are caught and logged so one misbehaving plugin does not crash others.

## Async Yielding
All backend event emissions include a small asynchronous yield after each callback and batch item. This `await asyncio.sleep(0.002)` pause (2 ms) ensures the event loop stays responsive by allowing other tasks to run between bus items.

## Events
The core combat engine emits a few global events that plugins may subscribe to:

- `damage_dealt(attacker, target, amount)`
- `damage_taken(target, attacker, amount)`
- `heal(healer, target, amount)`
- `heal_received(target, healer, amount)`
- `hit_landed(attacker, target, amount, source_type="attack", source_name=None)` - emitted when a successful hit occurs

Plugins can define additional event names as needed.
