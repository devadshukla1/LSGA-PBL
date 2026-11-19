"""Tests for summary statistics and paired comparison speedups."""

from src.benchmarks.benchmark_models import BenchmarkRunResult
from src.benchmarks.comparisons import compute_paired_comparisons
from src.benchmarks.statistics import compute_benchmark_summaries


def _create_mock_run(
    algo: str,
    time_ms: float,
    source: int = 0,
    target: int = 1,
    rep: int = 1,
    mode: str = "timing",
    mem_mb: float = 0.5,
) -> BenchmarkRunResult:
    return BenchmarkRunResult(
        experiment_id="exp_01",
        dataset_id="test_ds",
        dataset_origin="test",
        graph_size_label="N=10",
        node_count=10,
        edge_count=20,
        source=source,
        target=target,
        algorithm=algo,
        objective="distance",
        repetition=rep,
        random_seed=42,
        runtime_ns=int(time_ms * 1_000_000),
        runtime_ms=time_ms,
        nodes_expanded=5,
        edges_examined=8,
        route_found=True,
        route_valid=True,
        optimality_verified=True,
        route_cost=100.0,
        reference_cost=100.0,
        status="ok",
        peak_python_memory_mb=mem_mb if mode == "memory" else None,
        measurement_mode=mode,
    )


def test_compute_benchmark_summaries():
    runs = [
        _create_mock_run("dijkstra", 10.0, rep=1),
        _create_mock_run("dijkstra", 12.0, rep=2),
        _create_mock_run("dijkstra", 14.0, rep=3),
        _create_mock_run("dijkstra", 0.0, mode="memory", mem_mb=1.2),
    ]

    summaries = compute_benchmark_summaries(runs)
    assert len(summaries) == 1
    s = summaries[0]
    assert s.algorithm == "dijkstra"
    assert s.successful_runs == 3
    assert s.failed_runs == 0
    assert s.mean_runtime_ms == 12.0
    assert s.median_runtime_ms == 12.0
    assert s.mean_peak_memory_mb == 1.2
    assert s.route_validity_rate == 1.0
    assert s.optimality_verification_rate == 1.0


def test_compute_paired_comparisons():
    # Dijkstra: 10ms, A*: 5ms -> speedup 2.0x
    runs = [
        _create_mock_run("dijkstra", 10.0, source=0, target=1, rep=1),
        _create_mock_run("astar", 5.0, source=0, target=1, rep=1),
        _create_mock_run("dijkstra", 8.0, source=2, target=3, rep=1),
        _create_mock_run("astar", 4.0, source=2, target=3, rep=1),
    ]

    comparisons = compute_paired_comparisons(runs)
    assert len(comparisons) == 1
    c = comparisons[0]
    assert c.baseline_algorithm == "dijkstra"
    assert c.candidate_algorithm == "astar"
    assert c.comparison_count == 2
    assert c.mean_speedup == 2.0
    assert c.median_speedup == 2.0
