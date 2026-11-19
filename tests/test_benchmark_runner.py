"""Tests for benchmark runner orchestration and execution."""

from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.benchmark_runner import run_benchmarks
from src.graph.dataset_service import load


def test_run_benchmarks_execution():
    info = load()
    graph = info.graph

    cfg = BenchmarkConfig(
        dataset_id="offline_sample",
        graph_sizes=[10],
        algorithms=["dijkstra", "astar"],
        objectives=["distance"],
        query_count=3,
        repetitions=2,
        warmup_runs=1,
        memory_enabled=True,
        correctness_enabled=True,
    )

    raw, summaries, comparisons, datasets, manifest = run_benchmarks(graph, config=cfg)

    assert len(raw) > 0
    assert len(summaries) > 0
    assert manifest.dataset_id == "offline_sample"
    assert manifest.query_count == 3
    assert manifest.repetitions == 2

    # Check timing records
    timing_records = [r for r in raw if r.measurement_mode == "timing"]
    assert all(r.runtime_ns >= 0 for r in timing_records)
    assert all(r.route_valid is True for r in timing_records)
    assert all(r.optimality_verified is True for r in timing_records)

    # Check memory records
    mem_records = [r for r in raw if r.measurement_mode == "memory"]
    assert len(mem_records) > 0
    assert all(
        r.peak_python_memory_bytes is not None and r.peak_python_memory_bytes > 0
        for r in mem_records
    )
