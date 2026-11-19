"""Tests for memory measurement using tracemalloc."""

from src.benchmarks.memory_profiler import measure_peak_memory


def test_measure_peak_memory():
    def allocate_list():
        # Allocate ~1MB of integers
        return [i for i in range(250_000)]

    peak_bytes, peak_mb, data = measure_peak_memory(allocate_list)
    assert len(data) == 250_000
    assert peak_bytes > 0
    assert peak_mb > 0.0
    # ~250k ints in Python is typically between 1MB and 15MB
    assert peak_mb >= 0.5
