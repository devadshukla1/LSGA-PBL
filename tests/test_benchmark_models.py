"""Tests for benchmark configuration and record models."""

import pytest

from src.benchmarks.benchmark_models import (
    BenchmarkConfig,
    BenchmarkRunResult,
)


def test_valid_benchmark_config():
    cfg = BenchmarkConfig(
        dataset_id="offline_sample",
        graph_sizes=[10, 50],
        algorithms=["dijkstra", "astar"],
        objectives=["distance"],
        query_count=10,
        repetitions=2,
    )
    assert cfg.dataset_id == "offline_sample"
    assert cfg.query_count == 10
    assert cfg.repetitions == 2


def test_invalid_benchmark_config_rejection():
    with pytest.raises(ValueError, match="query_count must be >= 1"):
        BenchmarkConfig(query_count=0)

    with pytest.raises(ValueError, match="repetitions must be >= 1"):
        BenchmarkConfig(repetitions=0)

    with pytest.raises(ValueError, match="warmup_runs must be >= 0"):
        BenchmarkConfig(warmup_runs=-1)

    with pytest.raises(ValueError, match="algorithms cannot be empty"):
        BenchmarkConfig(algorithms=[])

    with pytest.raises(ValueError, match="Invalid algorithm"):
        BenchmarkConfig(algorithms=["nonexistent_algo"])

    with pytest.raises(ValueError, match="objectives cannot be empty"):
        BenchmarkConfig(objectives=[])

    with pytest.raises(ValueError, match="Invalid objective"):
        BenchmarkConfig(objectives=["unknown_obj"])


def test_benchmark_run_result_creation():
    res = BenchmarkRunResult(
        experiment_id="exp_01",
        dataset_id="sample",
        dataset_origin="offline",
        graph_size_label="N=16",
        node_count=16,
        edge_count=34,
        source=0,
        target=1,
        algorithm="dijkstra",
        objective="distance",
        repetition=1,
        random_seed=42,
        runtime_ns=150_000,
        runtime_ms=0.15,
        nodes_expanded=2,
        edges_examined=3,
        route_found=True,
        route_valid=True,
        optimality_verified=True,
        route_cost=100.0,
        reference_cost=100.0,
        absolute_cost_error=0.0,
        relative_cost_error=0.0,
    )
    assert res.experiment_id == "exp_01"
    assert res.runtime_ms == 0.15
    assert res.optimality_verified is True
