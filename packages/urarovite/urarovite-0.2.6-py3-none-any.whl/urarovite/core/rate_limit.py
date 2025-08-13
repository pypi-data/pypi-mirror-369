import time
from threading import Lock
from functools import wraps
from typing import Callable, TypeVar, Any, cast

F = TypeVar("F", bound=Callable[..., Any])

def rate_limited(max_calls: int = 59, period: float = 60.0) -> Callable[[F], F]:
    """
    Decorator to rate limit a function to `max_calls` within `period` seconds.
    Thread-safe. If the rate limit is reached, sleeps until a call is allowed.

    Args:
        max_calls: Maximum number of allowed calls within the period.
        period: Time window in seconds (default: 60.0).

    Returns:
        Decorated function that enforces the rate limit.
    """
    lock = Lock()
    call_times: list[float] = []

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal call_times
            now = time.time()
            with lock:
                # Remove calls outside the current window
                call_times = [t for t in call_times if now - t < period]
                if len(call_times) >= max_calls:
                    # Wait until the oldest call is outside the window
                    oldest = call_times[0]
                    wait_time = period - (now - oldest)
                    if wait_time > 0:
                        time.sleep(wait_time)
                    # After sleeping, update the call_times again
                    now = time.time()
                    call_times = [t for t in call_times if now - t < period]
                call_times.append(time.time())
            return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator
