"""Benchmarking framework for graph routing algorithms, scaling, and performance profiling."""

from src.benchmarks.benchmark_models import (
    BenchmarkComparison,
    BenchmarkConfig,
    BenchmarkDataset,
    BenchmarkManifest,
    BenchmarkQuery,
    BenchmarkRunResult,
    BenchmarkSummary,
)
from src.benchmarks.benchmark_runner import run_benchmarks
from src.benchmarks.comparisons import compute_paired_comparisons
from src.benchmarks.correctness import verify_route_correctness_and_optimality
from src.benchmarks.dataset_sampler import prepare_benchmark_datasets
from src.benchmarks.memory_profiler import measure_peak_memory
from src.benchmarks.partition_benchmarks import (
    PartitionBenchmarkReport,
    run_partition_benchmarks,
)
from src.benchmarks.query_generator import (
    generate_benchmark_queries,
    generate_unreachable_queries,
)
from src.benchmarks.report_export import (
    export_benchmark_results,
    list_saved_experiments,
    load_benchmark_experiment,
)
from src.benchmarks.statistics import compute_benchmark_summaries
from src.benchmarks.timing import compute_timing_summary, measure_runtime_ns

__all__ = [
    "BenchmarkComparison",
    "BenchmarkConfig",
    "BenchmarkDataset",
    "BenchmarkManifest",
    "BenchmarkQuery",
    "BenchmarkRunResult",
    "BenchmarkSummary",
    "PartitionBenchmarkReport",
    "compute_benchmark_summaries",
    "compute_paired_comparisons",
    "compute_timing_summary",
    "export_benchmark_results",
    "generate_benchmark_queries",
    "generate_unreachable_queries",
    "list_saved_experiments",
    "load_benchmark_experiment",
    "measure_peak_memory",
    "measure_runtime_ns",
    "prepare_benchmark_datasets",
    "run_benchmarks",
    "run_partition_benchmarks",
    "verify_route_correctness_and_optimality",
]
