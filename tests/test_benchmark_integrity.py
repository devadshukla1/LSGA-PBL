"""Tests for empirical benchmarking framework, query sampling, and statistical summaries."""

from scripts.generate_sample_graph import build_sample
from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.benchmark_runner import run_benchmarks
from src.benchmarks.query_generator import generate_benchmark_queries


def test_query_generator_reproducibility() -> None:
    """Verify benchmark queries are deterministic with fixed random seed."""
    graph = build_sample()
    q1 = generate_benchmark_queries(graph, count=5, seed=42)
    q2 = generate_benchmark_queries(graph, count=5, seed=42)

    assert q1 == q2
    assert len(q1) == 5
    for q in q1:
        assert q.source != q.target
        assert q.source in graph and q.target in graph


def test_benchmark_runner_full_correctness() -> None:
    """Verify benchmark runner produces 100% correct routes matching NetworkX oracle."""
    graph = build_sample()
    config = BenchmarkConfig(
        dataset_id="offline_sample",
        graph_sizes=[len(graph)],
        algorithms=["dijkstra", "astar", "bidirectional_dijkstra"],
        objectives=["distance"],
        query_count=3,
        repetitions=2,
        random_seed=42,
        memory_enabled=False,
        correctness_enabled=True,
    )
    raw, summaries, comparisons, datasets_meta, manifest = run_benchmarks(graph, config=config)

    assert len(raw) > 0
    assert len(summaries) == 3  # 3 algorithms for 1 size & 1 objective

    for s in summaries:
        assert s.route_validity_rate == 1.0, f"Algorithm {s.algorithm} had invalid routes"
        assert s.optimality_verification_rate == 1.0, f"Algorithm {s.algorithm} was suboptimal"
        assert s.mean_runtime_ms > 0
        assert s.median_runtime_ms > 0
        assert s.p95_runtime_ms >= s.median_runtime_ms
