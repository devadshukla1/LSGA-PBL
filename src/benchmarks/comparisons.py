"""Paired algorithm runtime speedup and efficiency comparisons."""

import statistics
from collections import defaultdict

from src.benchmarks.benchmark_models import BenchmarkComparison, BenchmarkRunResult

COMPARISON_PAIRS = (
    ("dijkstra", "astar"),
    ("dijkstra", "bidirectional_dijkstra"),
    ("astar", "bidirectional_dijkstra"),
)


def compute_paired_comparisons(
    raw_results: list[BenchmarkRunResult],
) -> list[BenchmarkComparison]:
    """Compute per-query paired speedup ratios between routing algorithms.

    Only pairs executing on the identical dataset, graph size, objective,
    query (source, target), and repetition are evaluated.
    Speedup is defined as: baseline_runtime_ns / candidate_runtime_ns.
    """
    # Group results by (dataset_id, graph_size_label, objective, source, target, repetition)
    grouped: dict[tuple, dict[str, BenchmarkRunResult]] = defaultdict(dict)

    for record in raw_results:
        if record.measurement_mode != "timing":
            continue
        if record.status != "ok" or not record.route_valid:
            continue
        key = (
            record.dataset_id,
            record.graph_size_label,
            record.objective,
            record.source,
            record.target,
            record.repetition,
        )
        grouped[key][record.algorithm] = record

    # Track speedup values per (baseline, candidate, dataset_id, graph_size_label, objective)
    speedup_records: dict[tuple[str, str, str, str, str], list[float]] = defaultdict(list)

    for (ds_id, size_label, obj, _s, _t, _rep), algos in grouped.items():
        for baseline, candidate in COMPARISON_PAIRS:
            if baseline in algos and candidate in algos:
                base_time = algos[baseline].runtime_ns
                cand_time = algos[candidate].runtime_ns
                if cand_time > 0 and base_time >= 0:
                    speedup = base_time / float(cand_time)
                    speedup_records[(baseline, candidate, ds_id, size_label, obj)].append(speedup)

    comparisons: list[BenchmarkComparison] = []
    for (baseline, candidate, ds_id, size_label, obj), speedups in sorted(speedup_records.items()):
        if not speedups:
            continue
        comparisons.append(
            BenchmarkComparison(
                baseline_algorithm=baseline,
                candidate_algorithm=candidate,
                dataset_id=ds_id,
                graph_size_label=size_label,
                objective=obj,
                comparison_count=len(speedups),
                mean_speedup=round(statistics.mean(speedups), 4),
                median_speedup=round(statistics.median(speedups), 4),
                min_speedup=round(min(speedups), 4),
                max_speedup=round(max(speedups), 4),
            )
        )

    return comparisons
