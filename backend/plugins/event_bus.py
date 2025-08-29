import asyncio
from collections import defaultdict
from collections.abc import Callable
import inspect
import logging
import time
from typing import Any
import weakref

try:
    from rich.logging import RichHandler
except Exception:  # pragma: no cover - fallback when Rich is missing
    RichHandler = logging.StreamHandler


class EventMetrics:
    """Track event bus performance metrics."""

    def __init__(self):
        self.event_counts = defaultdict(int)
        self.event_timings = defaultdict(list)
        self.slow_events = []  # Events that took >16ms (one frame at 60fps)
        self.error_counts = defaultdict(int)

    def record_event(self, event: str, duration: float, error: bool = False):
        self.event_counts[event] += 1
        self.event_timings[event].append(duration)

        if error:
            self.error_counts[event] += 1

        if duration > 0.016:  # >16ms may cause frame drops
            self.slow_events.append((event, duration, time.time()))

    def get_stats(self) -> dict:
        stats = {}
        for event, timings in self.event_timings.items():
            if timings:
                stats[event] = {
                    'count': len(timings),
                    'avg_time': sum(timings) / len(timings),
                    'max_time': max(timings),
                    'errors': self.error_counts[event]
                }
        return stats


class _Bus:
    def __init__(self) -> None:
        self._subs: dict[str, list[tuple[object, Callable[..., Any]]]] = defaultdict(list)
        self._metrics = EventMetrics()
        self._high_frequency_events = {'damage_dealt', 'damage_taken', 'hit_landed', 'heal_received'}
        self._batched_events = defaultdict(list)
        self._batch_timer = None
        self._batch_interval = 0.016  # Batch events for one frame (16ms at 60fps)

    def accept(self, event: str, obj, func: Callable[..., Any]) -> None:
        # Use weak references for objects to prevent memory leaks
        if obj is not None:
            obj_ref = weakref.ref(obj)
        else:
            obj_ref = None
        self._subs[event].append((obj_ref or obj, func))

    def ignore(self, event: str, obj) -> None:
        if obj is not None:
            # Use weak reference for comparison to handle object cleanup
            self._subs[event] = [
                pair for pair in self._subs.get(event, [])
                if pair[0] is not obj and (not callable(pair[0]) or pair[0]() is not obj)
            ]
        else:
            self._subs[event] = [
                pair for pair in self._subs.get(event, []) if pair[0] is not obj
            ]

    def send(self, event: str, args) -> None:
        """Synchronous send with performance monitoring and error isolation."""
        start_time = time.perf_counter()
        callbacks = list(self._subs.get(event, []))

        if not callbacks:
            return

        errors = 0
        for obj_ref, func in callbacks:
            try:
                # Handle weak references
                if callable(obj_ref):
                    obj = obj_ref()
                    if obj is None:  # Object was garbage collected
                        continue
                else:
                    obj = obj_ref

                func(*args)
            except Exception as e:
                errors += 1
                log.exception("Error in sync event callback for %s: %s", event, e)

        duration = time.perf_counter() - start_time
        self._metrics.record_event(event, duration, errors > 0)

        # Log performance warnings for slow events
        if duration > 0.050:  # >50ms is definitely problematic
            log.warning(f"Slow event emission: {event} took {duration*1000:.1f}ms with {len(callbacks)} subscribers")

    def send_batched(self, event: str, args) -> None:
        """Add event to batch for high-frequency events."""
        self._batched_events[event].append(args)

        if self._batch_timer is None:
            # Schedule batch processing
            self._batch_timer = asyncio.create_task(self._process_batches())

    async def _process_batches(self):
        """Process batched events after a short delay."""
        await asyncio.sleep(self._batch_interval)

        for event, args_list in self._batched_events.items():
            if args_list:
                # Process all batched events of this type
                await self.send_async(event, args_list[-1])  # Only process the latest for performance

        self._batched_events.clear()
        self._batch_timer = None

    async def send_async(self, event: str, args) -> None:
        """Async version of send that executes callbacks concurrently with error isolation."""
        start_time = time.perf_counter()
        callbacks = list(self._subs.get(event, []))

        if not callbacks:
            return

        async def _run_callback(obj_ref, func, args):
            try:
                # Handle weak references
                if callable(obj_ref):
                    obj = obj_ref()
                    if obj is None:  # Object was garbage collected
                        return False
                else:
                    obj = obj_ref

                if inspect.iscoroutinefunction(func):
                    await func(*args)
                else:
                    # Run sync functions in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, lambda: func(*args))
                return True
            except Exception as e:
                log.exception("Error in async event callback for %s: %s", event, e)
                return False

        # Run all callbacks concurrently to avoid blocking
        results = await asyncio.gather(
            *[_run_callback(obj_ref, func, args) for obj_ref, func in callbacks],
            return_exceptions=True
        )

        duration = time.perf_counter() - start_time
        errors = sum(1 for r in results if r is False or isinstance(r, Exception))
        self._metrics.record_event(event, duration, errors > 0)

    def get_metrics(self) -> dict:
        """Get performance metrics for monitoring."""
        return self._metrics.get_stats()

    def clear_metrics(self) -> None:
        """Clear metrics (useful for testing)."""
        self._metrics = EventMetrics()


bus = _Bus()

log = logging.getLogger(__name__)
if not log.handlers:
    log.addHandler(RichHandler())


class EventBus:
    def __init__(self):
        self._prefer_async = True  # Prefer async emission when possible
        self._performance_monitoring = True

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
        """Emit event synchronously. Use emit_async for better performance when possible."""
        bus.send(event, args)

    async def emit_async(self, event: str, *args: Any) -> None:
        """Async version of emit that executes callbacks concurrently"""
        await bus.send_async(event, args)

    def emit_batched(self, event: str, *args: Any) -> None:
        """Emit high-frequency events in batches to reduce blocking."""
        bus.send_batched(event, args)

    def get_performance_metrics(self) -> dict:
        """Get event bus performance metrics."""
        return bus.get_metrics()

    def clear_metrics(self) -> None:
        """Clear performance metrics."""
        bus.clear_metrics()

    def set_async_preference(self, prefer_async: bool) -> None:
        """Set whether to prefer async emission when possible."""
        self._prefer_async = prefer_async
