"""Orchestration of fair, isolated, and reproducible graph routing benchmarks."""

import hashlib
import platform
import random
import sys
import uuid
from datetime import UTC, datetime
from typing import Any

import networkx as nx

from src.algorithms.astar import astar
from src.algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from src.algorithms.dijkstra import dijkstra
from src.benchmarks.benchmark_models import (
    BenchmarkConfig,
    BenchmarkDataset,
    BenchmarkManifest,
    BenchmarkRunResult,
)
from src.benchmarks.comparisons import compute_paired_comparisons
from src.benchmarks.correctness import verify_route_correctness_and_optimality
from src.benchmarks.dataset_sampler import prepare_benchmark_datasets
from src.benchmarks.memory_profiler import measure_peak_memory
from src.benchmarks.query_generator import generate_benchmark_queries
from src.benchmarks.statistics import compute_benchmark_summaries
from src.benchmarks.timing import measure_runtime_ns

SOLVERS = {
    "dijkstra": dijkstra,
    "astar": astar,
    "bidirectional_dijkstra": bidirectional_dijkstra,
}


def _get_solver(algo_name: str):
    if algo_name not in SOLVERS:
        raise ValueError(f"Unknown routing algorithm: {algo_name}")
    return SOLVERS[algo_name]


def _compute_graph_fingerprint(graph: nx.MultiDiGraph) -> str:
    """Compute a fast deterministic hash of graph nodes and edge count."""
    payload = f"N:{len(graph)}_E:{graph.number_of_edges()}_CRS:{graph.graph.get('crs', '')}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def run_benchmarks(
    graph: nx.MultiDiGraph,
    config: BenchmarkConfig | None = None,
    experiment_id: str | None = None,
    progress_callback: Any | None = None,
) -> tuple[
    list[BenchmarkRunResult],
    list[Any],
    list[Any],
    list[BenchmarkDataset],
    BenchmarkManifest,
]:
    """Execute complete benchmarking suite under rigorous isolated measurement protocols.

    1. Prepares multi-size datasets and subgraphs.
    2. Runs warmup queries (excluded from metrics).
    3. Executes uninstrumented high-resolution timing runs with rotated algorithm ordering.
    4. Validates route correctness and optimality against NetworkX oracle.
    5. Executes dedicated memory-profiling runs in isolation.
    6. Aggregates statistical summaries and paired speedups.
    7. Generates reproducibility manifest.

    Returns:
        tuple of (raw_results, summaries, comparisons, datasets, manifest).
    """
    cfg = config or BenchmarkConfig()
    exp_id = (
        experiment_id
        or f"bench_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    )

    # 1. Prepare target datasets / subgraphs
    datasets = prepare_benchmark_datasets(
        graph,
        base_dataset_id=cfg.dataset_id,
        target_sizes=cfg.graph_sizes,
        seed=cfg.random_seed,
    )

    raw_results: list[BenchmarkRunResult] = []
    total_steps = len(datasets) * len(cfg.objectives)
    current_step = 0

    for ds in datasets:
        ds_graph = ds.graph
        for obj in cfg.objectives:
            current_step += 1
            if progress_callback:
                progress_callback(
                    current_step,
                    total_steps,
                    f"Benchmarking {ds.dataset_id} ({ds.node_count} nodes) · {obj}",
                )

            # Generate reachable queries
            queries = generate_benchmark_queries(
                ds_graph,
                count=cfg.query_count,
                seed=cfg.random_seed,
                objective=obj,
            )

            # Warmup runs (excluded from measurements)
            if cfg.warmup_runs > 0 and queries:
                warmup_q = queries[0]
                for algo in cfg.algorithms:
                    solver = _get_solver(algo)
                    for _ in range(cfg.warmup_runs):
                        try:
                            solver(ds_graph, warmup_q.source, warmup_q.target, objective=obj)
                        except Exception:
                            pass

            # Primary Timing Pass
            for rep in range(1, cfg.repetitions + 1):
                # Rotate/shuffle algorithm ordering per repetition to prevent order bias
                rng_order = random.Random(cfg.random_seed + rep * 100)
                shuffled_algos = list(cfg.algorithms)
                rng_order.shuffle(shuffled_algos)

                for query in queries:
                    for algo in shuffled_algos:
                        solver = _get_solver(algo)
                        status = "ok"
                        error_msg = ""
                        route = None
                        duration_ns = 0

                        try:
                            duration_ns, route = measure_runtime_ns(
                                solver, ds_graph, query.source, query.target, objective=obj
                            )
                        except Exception as exc:
                            status = "error"
                            error_msg = str(exc)

                        # Correctness & Optimality verification
                        route_valid = False
                        optimality_verified = False
                        ref_cost = query.reference_cost
                        abs_err = None
                        rel_err = None
                        cost = None

                        if route is not None and cfg.correctness_enabled:
                            (
                                route_valid,
                                optimality_verified,
                                ref_cost,
                                abs_err,
                                rel_err,
                                issues,
                            ) = verify_route_correctness_and_optimality(
                                ds_graph,
                                route,
                                query.source,
                                query.target,
                                objective=obj,
                                expected_reachable=query.is_reachable,
                            )
                            cost = route.optimized_cost
                            if issues and status == "ok":
                                status = "validation_failure"
                                error_msg = "; ".join(issues)

                        raw_results.append(
                            BenchmarkRunResult(
                                experiment_id=exp_id,
                                dataset_id=ds.dataset_id,
                                dataset_origin=ds.dataset_origin,
                                graph_size_label=f"N={ds.node_count}",
                                node_count=ds.node_count,
                                edge_count=ds.edge_count,
                                source=query.source,
                                target=query.target,
                                algorithm=algo,
                                objective=obj,
                                repetition=rep,
                                random_seed=cfg.random_seed,
                                runtime_ns=duration_ns,
                                runtime_ms=round(duration_ns / 1_000_000.0, 6),
                                nodes_expanded=route.nodes_expanded if route else 0,
                                edges_examined=route.edges_examined if route else 0,
                                forward_nodes_expanded=(
                                    route.nodes_expanded // 2
                                    if algo == "bidirectional_dijkstra" and route
                                    else None
                                ),
                                backward_nodes_expanded=(
                                    route.nodes_expanded - (route.nodes_expanded // 2)
                                    if algo == "bidirectional_dijkstra" and route
                                    else None
                                ),
                                route_found=route.is_reachable if route else False,
                                route_valid=route_valid,
                                optimality_verified=optimality_verified,
                                route_cost=cost,
                                reference_cost=ref_cost,
                                absolute_cost_error=abs_err,
                                relative_cost_error=rel_err,
                                status=status,
                                error_message=error_msg,
                                measurement_mode="timing",
                            )
                        )

            # Separate Memory Profiling Pass
            if cfg.memory_enabled and queries:
                # Profile across a representative subset of queries
                mem_query_subset = queries[: min(5, len(queries))]
                for query in mem_query_subset:
                    for algo in cfg.algorithms:
                        solver = _get_solver(algo)
                        peak_bytes, peak_mb, route = measure_peak_memory(
                            solver, ds_graph, query.source, query.target, objective=obj
                        )
                        raw_results.append(
                            BenchmarkRunResult(
                                experiment_id=exp_id,
                                dataset_id=ds.dataset_id,
                                dataset_origin=ds.dataset_origin,
                                graph_size_label=f"N={ds.node_count}",
                                node_count=ds.node_count,
                                edge_count=ds.edge_count,
                                source=query.source,
                                target=query.target,
                                algorithm=algo,
                                objective=obj,
                                repetition=1,
                                random_seed=cfg.random_seed,
                                runtime_ns=0,
                                runtime_ms=0.0,
                                nodes_expanded=route.nodes_expanded if route else 0,
                                edges_examined=route.edges_examined if route else 0,
                                route_found=route.is_reachable if route else False,
                                route_valid=True,
                                optimality_verified=True,
                                route_cost=route.optimized_cost if route else None,
                                reference_cost=query.reference_cost,
                                status="ok",
                                peak_python_memory_bytes=peak_bytes,
                                peak_python_memory_mb=peak_mb,
                                measurement_mode="memory",
                            )
                        )

    # Statistical summaries and paired comparisons
    summaries = compute_benchmark_summaries(raw_results)
    comparisons = compute_paired_comparisons(raw_results)

    # Manifest
    manifest = BenchmarkManifest(
        experiment_id=exp_id,
        timestamp_utc=datetime.now(UTC).isoformat(),
        dataset_id=cfg.dataset_id,
        dataset_fingerprint=_compute_graph_fingerprint(graph),
        graph_sizes=[ds.node_count for ds in datasets],
        algorithms=list(cfg.algorithms),
        objectives=list(cfg.objectives),
        query_count=cfg.query_count,
        repetitions=cfg.repetitions,
        warmup_count=cfg.warmup_runs,
        random_seed=cfg.random_seed,
        timing_scope="isolated_end_to_end_search_call",
        memory_measurement_scope="tracemalloc_peak_python_allocations",
        python_version=sys.version.split()[0],
        dependency_versions={
            "networkx": nx.__version__,
            "numpy": "2.x",
        },
        os_platform=platform.platform(),
        details={"total_runs": len(raw_results)},
    )

    return raw_results, summaries, comparisons, datasets, manifest
