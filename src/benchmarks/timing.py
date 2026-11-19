"""High-resolution runtime measurement and timing aggregation."""

import statistics
import time
from collections.abc import Callable
from typing import Any

import numpy as np


def measure_runtime_ns(func: Callable[..., Any], *args: Any, **kwargs: Any) -> tuple[int, Any]:
    """Execute a function and return its duration in nanoseconds alongside the result.

    Uses time.perf_counter_ns() for monotonic high-resolution timing.
    """
    start_ns = time.perf_counter_ns()
    result = func(*args, **kwargs)
    duration_ns = time.perf_counter_ns() - start_ns
    return duration_ns, result


def compute_timing_summary(durations_ms: list[float]) -> dict[str, float]:
    """Compute summary statistics for a collection of runtime measurements in milliseconds.

    Returns:
        dict containing mean, median, sample std (or 0.0 if N<2), min, max, and p95.
    """
    if not durations_ms:
        return {
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "p95": 0.0,
        }

    mean_val = statistics.mean(durations_ms)
    median_val = statistics.median(durations_ms)
    std_val = statistics.stdev(durations_ms) if len(durations_ms) > 1 else 0.0
    min_val = min(durations_ms)
    max_val = max(durations_ms)
    p95_val = float(np.percentile(durations_ms, 95))

    return {
        "mean": round(mean_val, 6),
        "median": round(median_val, 6),
        "std": round(std_val, 6),
        "min": round(min_val, 6),
        "max": round(max_val, 6),
        "p95": round(p95_val, 6),
    }
