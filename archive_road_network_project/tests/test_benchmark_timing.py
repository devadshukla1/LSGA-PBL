"""Tests for timing measurement and statistical aggregation."""

import time

from src.benchmarks.timing import compute_timing_summary, measure_runtime_ns


def test_measure_runtime_ns():
    def dummy_task():
        time.sleep(0.005)
        return "completed"

    duration_ns, result = measure_runtime_ns(dummy_task)
    assert result == "completed"
    assert duration_ns > 0
    # ~5ms should be at least 4,000,000 ns
    assert duration_ns >= 4_000_000


def test_compute_timing_summary_metrics():
    # Known test values
    samples = [10.0, 12.0, 14.0, 16.0, 18.0]
    summary = compute_timing_summary(samples)

    assert summary["mean"] == 14.0
    assert summary["median"] == 14.0
    assert summary["min"] == 10.0
    assert summary["max"] == 18.0
    assert summary["p95"] > 14.0
    assert summary["std"] > 0.0


def test_compute_timing_summary_empty_and_single():
    empty_res = compute_timing_summary([])
    assert empty_res["mean"] == 0.0
    assert empty_res["std"] == 0.0

    single_res = compute_timing_summary([5.5])
    assert single_res["mean"] == 5.5
    assert single_res["std"] == 0.0
