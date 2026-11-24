"""Memory profiling using tracemalloc for peak Python-tracked memory measurement."""

import tracemalloc
from collections.abc import Callable
from typing import Any


def measure_peak_memory(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> tuple[int, float, Any]:
    """Execute a function under tracemalloc to record peak Python-tracked memory.

    Note:
        tracemalloc profiles Python memory allocations; it does not measure C-extension
        buffers or total operating system resident set size (RSS).

    Returns:
        tuple of (peak_memory_bytes, peak_memory_mb, function_result).
    """
    tracemalloc.start()
    tracemalloc.reset_peak()
    try:
        result = func(*args, **kwargs)
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    peak_mb = round(peak_bytes / (1024.0 * 1024.0), 6)
    return peak_bytes, peak_mb, result
