"""Statistical aggregation of benchmark execution records."""

import statistics
from collections import defaultdict

import numpy as np

from src.benchmarks.benchmark_models import BenchmarkRunResult, BenchmarkSummary


def compute_benchmark_summaries(
    raw_results: list[BenchmarkRunResult],
) -> list[BenchmarkSummary]:
    """Aggregate raw execution records by dataset, graph size, algorithm, and objective."""
    grouped: dict[tuple[str, str, int, str, str], list[BenchmarkRunResult]] = defaultdict(list)

    for r in raw_results:
        key = (r.dataset_id, r.graph_size_label, r.node_count, r.algorithm, r.objective)
        grouped[key].append(r)

    summaries: list[BenchmarkSummary] = []

    for (ds_id, size_label, node_count, algo, obj), records in sorted(grouped.items()):
        timing_records = [r for r in records if r.measurement_mode == "timing"]
        memory_records = [r for r in records if r.measurement_mode == "memory"]

        successful_timing = [r for r in timing_records if r.status == "ok" and r.route_valid]
        failed_count = sum(1 for r in timing_records if r.status != "ok" or not r.route_valid)

        durations = [r.runtime_ms for r in successful_timing]
        nodes_expanded = [r.nodes_expanded for r in successful_timing]
        edges_examined = [r.edges_examined for r in successful_timing]

        mean_time = statistics.mean(durations) if durations else 0.0
        median_time = statistics.median(durations) if durations else 0.0
        std_time = statistics.stdev(durations) if len(durations) > 1 else 0.0
        min_time = min(durations) if durations else 0.0
        max_time = max(durations) if durations else 0.0
        p95_time = float(np.percentile(durations, 95)) if durations else 0.0

        mean_nodes = statistics.mean(nodes_expanded) if nodes_expanded else 0.0
        mean_edges = statistics.mean(edges_examined) if edges_examined else 0.0

        # Memory stats
        memories = [
            r.peak_python_memory_mb for r in memory_records if r.peak_python_memory_mb is not None
        ]
        mean_mem = statistics.mean(memories) if memories else 0.0

        # Correctness rates
        total_eval = len(timing_records)
        valid_count = sum(1 for r in timing_records if r.route_valid)
        optimal_count = sum(1 for r in timing_records if r.optimality_verified)

        valid_rate = (valid_count / total_eval) if total_eval > 0 else 0.0
        optimal_rate = (optimal_count / total_eval) if total_eval > 0 else 0.0

        # Unique queries count
        unique_queries = len({(r.source, r.target) for r in timing_records})

        summaries.append(
            BenchmarkSummary(
                dataset_id=ds_id,
                graph_size_label=size_label,
                node_count=node_count,
                algorithm=algo,
                objective=obj,
                query_count=unique_queries,
                successful_runs=len(successful_timing),
                failed_runs=failed_count,
                mean_runtime_ms=round(mean_time, 4),
                median_runtime_ms=round(median_time, 4),
                std_runtime_ms=round(std_time, 4),
                min_runtime_ms=round(min_time, 4),
                max_runtime_ms=round(max_time, 4),
                p95_runtime_ms=round(p95_time, 4),
                mean_nodes_expanded=round(mean_nodes, 2),
                mean_edges_examined=round(mean_edges, 2),
                mean_peak_memory_mb=round(mean_mem, 4),
                route_validity_rate=round(valid_rate, 4),
                optimality_verification_rate=round(optimal_rate, 4),
            )
        )

    return summaries
