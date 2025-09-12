import asyncio
from collections import defaultdict
from collections.abc import Callable
import contextlib
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
        self._dynamic_batch_interval = True  # Enable adaptive batching

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

                if inspect.iscoroutinefunction(func):
                    loop = None
                    with contextlib.suppress(RuntimeError):
                        loop = asyncio.get_running_loop()
                    if loop is not None:
                        loop.create_task(func(*args))
                    else:
                        log.warning(
                            "Async callback %s called from sync context with no event loop",
                            func,
                        )
                else:
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
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                log.debug("No running event loop; processing batched events synchronously")
                self._process_batches_sync()
            else:
                # Adaptive batching: reduce interval under high load
                if self._dynamic_batch_interval:
                    total_queued = sum(len(events) for events in self._batched_events.values())
                    if total_queued > 100:
                        interval = 0.001  # Very fast processing under very high load
                    elif total_queued > 50:
                        interval = max(0.005, self._batch_interval * 0.5)  # Faster processing under load
                    else:
                        interval = self._batch_interval
                else:
                    interval = self._batch_interval

                # Schedule batch processing
                self._batch_timer = loop.create_task(
                    self._process_batches_with_interval(interval)
                )
                return

    async def _process_batches_with_interval(self, interval: float):
        """Process batched events with adaptive interval."""
        await asyncio.sleep(interval)
        await self._process_batches_internal()

    async def _process_batches(self):
        """Process batched events with default interval."""
        await asyncio.sleep(self._batch_interval)
        await self._process_batches_internal()

    async def _process_batches_internal(self):
        """Internal method to process batched events concurrently."""
        # Collect all batched events and process them concurrently
        all_events = []

        # Snapshot current batches to avoid mutation during async yield
        events_snapshot = list(self._batched_events.items())

        # Clear batches immediately so new events can be scheduled separately
        self._batched_events.clear()
        self._batch_timer = None

        for event, args_list in events_snapshot:
            for args in args_list:
                all_events.append((event, args))
                await asyncio.sleep(0.002)

        if all_events:
            # Process all events concurrently for much better performance
            async def process_single_event(event_data):
                event, args = event_data
                try:
                    await self.send_async(event, args)
                except Exception as e:
                    log.exception("Error processing batched event %s: %s", event, e)
                await asyncio.sleep(0.002)

            # Use gather with limited concurrency to avoid overwhelming the event loop
            batch_size = 100  # Process in chunks to manage memory and concurrency
            for i in range(0, len(all_events), batch_size):
                batch = all_events[i:i + batch_size]
                await asyncio.gather(
                    *[process_single_event(event_data) for event_data in batch],
                    return_exceptions=True,
                )
                await asyncio.sleep(0.002)

    def _process_batches_sync(self):
        """Fallback sync processing when no event loop is available."""
        # Mark processing to avoid re-entrant batch processing
        self._batch_timer = True
        try:
            while self._batched_events:
                # Take a snapshot to avoid RuntimeError if new events are added
                events = list(self._batched_events.items())
                # Clear the original dict; new events will repopulate it
                self._batched_events.clear()
                for event, args_list in events:
                    for args in args_list:
                        try:
                            self.send(event, args)
                        except Exception as e:
                            log.exception("Error processing sync batched event %s: %s", event, e)
        finally:
            # Clear timer when all events have been processed
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
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(None, lambda: func(*args))
                await asyncio.sleep(0.002)
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
        def _prepare_args(args: Any) -> list[Any]:
            sig = inspect.signature(callback)
            params = [
                p
                for p in sig.parameters.values()
                if p.kind
                in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            ]
            accepts_varargs = any(
                p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values()
            )

            call_args = list(args)
            if not accepts_varargs:
                if len(call_args) > len(params):
                    call_args = call_args[: len(params)]
                required = [
                    p for p in params if p.default is inspect.Parameter.empty
                ]
                if len(call_args) < len(required):
                    call_args.extend([None] * (len(required) - len(call_args)))

            return call_args

        if inspect.iscoroutinefunction(callback):
            async def wrapper(*args: Any) -> None:
                try:
                    call_args = _prepare_args(args)
                    await callback(*call_args)
                except Exception:
                    log.exception("Error in '%s' subscriber %s", event, callback)

        else:
            def wrapper(*args: Any) -> None:
                try:
                    call_args = _prepare_args(args)
                    callback(*call_args)
                except Exception:
                    log.exception("Error in '%s' subscriber %s", event, callback)

        bus.accept(event, callback, wrapper)

    def unsubscribe(self, event: str, callback: Callable[..., Any]) -> None:
        bus.ignore(event, callback)

    def emit(self, event: str, *args: Any) -> None:
        """Emit event. Prefers async emission when enabled for better performance."""
        if self._prefer_async:
            try:
                # Check if we're in an async context
                asyncio.get_running_loop()
                # When async is preferred and event loop is available, use batching for better performance
                bus.send_batched(event, args)
            except RuntimeError:
                # No event loop, fall back to sync emission
                bus.send(event, args)
        else:
            # Traditional sync emission
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

    def set_dynamic_batching(self, enabled: bool) -> None:
        """Enable or disable dynamic batching based on load."""
        bus._dynamic_batch_interval = enabled

    def set_batch_interval(self, interval: float) -> None:
        """Set the default batch interval in seconds."""
        bus._batch_interval = max(0.001, interval)  # Minimum 1ms
