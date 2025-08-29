import asyncio
from collections import defaultdict
from collections.abc import Callable
import inspect
import logging
from typing import Any

try:
    from rich.logging import RichHandler
except Exception:  # pragma: no cover - fallback when Rich is missing
    RichHandler = logging.StreamHandler


class _Bus:
    def __init__(self) -> None:
        self._subs: dict[str, list[tuple[object, Callable[..., Any]]]] = defaultdict(list)

    def accept(self, event: str, obj, func: Callable[..., Any]) -> None:
        self._subs[event].append((obj, func))

    def ignore(self, event: str, obj) -> None:
        self._subs[event] = [
            pair for pair in self._subs.get(event, []) if pair[0] is not obj
        ]

    def send(self, event: str, args) -> None:
        for _, func in list(self._subs.get(event, [])):
            func(*args)

    async def send_async(self, event: str, args) -> None:
        """Async version of send that executes callbacks concurrently"""
        callbacks = list(self._subs.get(event, []))
        if not callbacks:
            return

        async def _run_callback(func, args):
            try:
                if inspect.iscoroutinefunction(func):
                    await func(*args)
                else:
                    func(*args)
            except Exception as e:
                log.exception("Error in async event callback: %s", e)

        # Run all callbacks concurrently to avoid blocking
        await asyncio.gather(*[_run_callback(func, args) for _, func in callbacks], return_exceptions=True)


bus = _Bus()

log = logging.getLogger(__name__)
if not log.handlers:
    log.addHandler(RichHandler())


class EventBus:
    def subscribe(self, event: str, callback: Callable[..., Any]) -> None:
        def wrapper(*args: Any) -> None:
            try:
                callback(*args)
            except Exception:
                log.exception("Error in '%s' subscriber %s", event, callback)

        bus.accept(event, callback, wrapper)

    def unsubscribe(self, event: str, callback: Callable[..., Any]) -> None:
        bus.ignore(event, callback)

    def emit(self, event: str, *args: Any) -> None:
        bus.send(event, args)

    async def emit_async(self, event: str, *args: Any) -> None:
        """Async version of emit that executes callbacks concurrently"""
        await bus.send_async(event, args)
