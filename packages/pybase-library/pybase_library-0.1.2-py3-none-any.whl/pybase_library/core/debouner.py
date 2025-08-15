import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import Any


class Debouner(ABC):
    """Abstract base class for debounce implementations."""

    @abstractmethod
    def debounce(self, delay: float, key: str | None = None) -> Callable:
        """Create a debounce decorator.

        Args:
            delay: Delay in seconds before function execution
            key: Optional key to group debounced calls

        Returns:
            Decorator function
        """
        pass


class MemoryDebouner(Debouner):
    """In-memory debounce implementation using threading timers."""

    def __init__(self) -> None:
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def debounce(self, delay: float, key: str | None = None) -> Callable:
        """Create a debounce decorator that delays function execution.

        Args:
            delay: Delay in seconds before function execution
            key: Optional key to group debounced calls. If None, uses function name

        Returns:
            Decorated function
        """

        def decorator(func: Callable) -> Callable:
            debounce_key = key or f"{func.__module__}.{func.__name__}"

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> None:
                with self._lock:
                    # Cancel existing timer if any
                    if debounce_key in self._timers:
                        self._timers[debounce_key].cancel()

                    # Create new timer
                    timer = threading.Timer(delay, func, args, kwargs)
                    self._timers[debounce_key] = timer
                    timer.start()

                    # Clean up finished timer
                    def cleanup() -> None:
                        with self._lock:
                            if debounce_key in self._timers:
                                del self._timers[debounce_key]

                    # Schedule cleanup after execution
                    cleanup_timer = threading.Timer(delay + 0.1, cleanup)
                    cleanup_timer.start()

            return wrapper

        return decorator

    def cancel_all(self) -> None:
        """Cancel all pending debounced calls."""
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()

    def cancel(self, key: str) -> bool:
        """Cancel a specific debounced call.

        Args:
            key: The debounce key to cancel

        Returns:
            True if timer was found and cancelled, False otherwise
        """
        with self._lock:
            if key in self._timers:
                self._timers[key].cancel()
                del self._timers[key]
                return True
            return False


class ThrottleDebouner(Debouner):
    """Throttle-based debounce implementation that limits execution frequency."""

    def __init__(self) -> None:
        self._last_called: dict[str, float] = {}
        self._lock = threading.Lock()

    def debounce(self, delay: float, key: str | None = None) -> Callable:
        """Create a throttle decorator that limits function execution frequency.

        Args:
            delay: Minimum delay in seconds between function executions
            key: Optional key to group throttled calls. If None, uses function name

        Returns:
            Decorated function
        """

        def decorator(func: Callable) -> Callable:
            throttle_key = key or f"{func.__module__}.{func.__name__}"

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self._lock:
                    now = time.time()
                    last_called = self._last_called.get(throttle_key, 0)

                    if now - last_called >= delay:
                        self._last_called[throttle_key] = now
                        return func(*args, **kwargs)
                    # If called too soon, ignore the call
                    return None

            return wrapper

        return decorator

    def reset(self, key: str | None = None) -> None:
        """Reset throttle state.

        Args:
            key: Specific key to reset. If None, resets all.
        """
        with self._lock:
            if key:
                self._last_called.pop(key, None)
            else:
                self._last_called.clear()


# Default global debouncer instance
_default_debouncer = MemoryDebouner()


def debounce(delay: float, key: str | None = None) -> Callable:
    """Convenience decorator for debouncing function calls.
    Args:
        delay: Delay in seconds before function execution
        key: Optional key to group debounced calls
    Returns:
        Decorated function
    Example:
        @debounce(0.5)
        def search(query: str):
            print(f"Searching for: {query}")
    """
    return _default_debouncer.debounce(delay, key)


def throttle(delay: float, key: str | None = None) -> Callable:
    """Convenience decorator for throttling function calls.
    Args:
        delay: Minimum delay in seconds between function executions
        key: Optional key to group throttled calls
    Returns:
        Decorated function
    Example:
        @throttle(1.0)
        def api_call():
            print("Making API call")
    """
    throttler = ThrottleDebouner()
    return throttler.debounce(delay, key)


# Export public API
__all__ = ["Debouner", "MemoryDebouner", "ThrottleDebouner", "debounce", "throttle"]
