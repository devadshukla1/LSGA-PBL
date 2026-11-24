"""Tests for benchmark CSV exports and manifest generation."""

from pathlib import Path
from tempfile import TemporaryDirectory

from src.benchmarks.benchmark_models import (
    BenchmarkComparison,
    BenchmarkDataset,
    BenchmarkManifest,
    BenchmarkRunResult,
    BenchmarkSummary,
)
from src.benchmarks.report_export import (
    export_benchmark_results,
    list_saved_experiments,
    load_benchmark_experiment,
)
from src.graph.dataset_service import load


def test_export_and_load_benchmark_results():
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Mock objects
        run = BenchmarkRunResult(
            experiment_id="test_exp",
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
            runtime_ns=100_000,
            runtime_ms=0.1,
            nodes_expanded=2,
            edges_examined=3,
            route_found=True,
            route_valid=True,
            optimality_verified=True,
            route_cost=100.0,
            reference_cost=100.0,
            status="ok",
        )
        summary = BenchmarkSummary(
            dataset_id="sample",
            graph_size_label="N=16",
            node_count=16,
            algorithm="dijkstra",
            objective="distance",
            query_count=1,
            successful_runs=1,
            failed_runs=0,
            mean_runtime_ms=0.1,
            median_runtime_ms=0.1,
            std_runtime_ms=0.0,
            min_runtime_ms=0.1,
            max_runtime_ms=0.1,
            p95_runtime_ms=0.1,
            mean_nodes_expanded=2.0,
            mean_edges_examined=3.0,
            mean_peak_memory_mb=0.5,
            route_validity_rate=1.0,
            optimality_verification_rate=1.0,
        )
        comparison = BenchmarkComparison(
            baseline_algorithm="dijkstra",
            candidate_algorithm="astar",
            dataset_id="sample",
            graph_size_label="N=16",
            objective="distance",
            comparison_count=1,
            mean_speedup=1.5,
            median_speedup=1.5,
            min_speedup=1.5,
            max_speedup=1.5,
        )
        graph = load().graph
        dataset_meta = BenchmarkDataset(
            dataset_id="sample",
            dataset_origin="offline",
            node_count=16,
            edge_count=34,
            directed_density=0.14,
            weak_component_count=1,
            strong_component_count=1,
            sampling_method="full",
            random_seed=42,
            graph=graph,
        )
        manifest = BenchmarkManifest(
            experiment_id="test_exp",
            timestamp_utc="2026-11-19T12:00:00Z",
            dataset_id="sample",
            dataset_fingerprint="abc123",
            graph_sizes=[16],
            algorithms=["dijkstra"],
            objectives=["distance"],
            query_count=1,
            repetitions=1,
            warmup_count=0,
            random_seed=42,
            timing_scope="isolated",
            memory_measurement_scope="tracemalloc",
            python_version="3.11",
            dependency_versions={"networkx": "3.4"},
            os_platform="Windows",
        )

        out = export_benchmark_results(
            [run], [summary], [comparison], [dataset_meta], manifest, output_directory=tmp_path
        )
        assert (out / "benchmark_raw.csv").is_file()
        assert (out / "benchmark_summary.csv").is_file()
        assert (out / "benchmark_comparisons.csv").is_file()
        assert (out / "benchmark_correctness.csv").is_file()
        assert (out / "benchmark_datasets.csv").is_file()
        assert (out / "benchmark_manifest.json").is_file()

        loaded = load_benchmark_experiment(out)
        assert len(loaded["raw"]) == 1
        assert len(loaded["summary"]) == 1
        assert loaded["manifest"]["experiment_id"] == "test_exp"

        exps = list_saved_experiments(tmp_path.parent)
        assert any(e["id"] == "test_exp" for e in exps)
