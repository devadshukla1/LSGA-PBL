"""Offline verification script for algorithm benchmarking, profiling, and export integrity."""

import copy
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.algorithms.astar import astar
from src.algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from src.algorithms.dijkstra import dijkstra
from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.benchmark_runner import run_benchmarks
from src.benchmarks.correctness import verify_route_correctness_and_optimality
from src.benchmarks.memory_profiler import measure_peak_memory
from src.benchmarks.query_generator import generate_benchmark_queries
from src.benchmarks.report_export import export_benchmark_results, load_benchmark_experiment
from src.graph.dataset_service import load
from src.graph.validation import validate


def main() -> int:
    print("=" * 65)
    print("SMART CITY TRAFFIC & EMERGENCY ROUTE OPTIMIZER")
    print("PHASE 9: Benchmarking & Algorithm Evaluation Verification")
    print("=" * 65)

    # 1. Load offline sample dataset
    info = load()
    graph = info.graph
    print(
        f"Loaded dataset: {info.metadata.dataset_name} "
        f"({len(graph)} nodes, {graph.number_of_edges()} edges)"
    )

    # Snapshot to verify immutability
    nodes_snapshot = copy.deepcopy(dict(graph.nodes(data=True)))
    edges_snapshot = copy.deepcopy(list(graph.edges(keys=True, data=True)))

    # 2. Validate graph
    val_report = validate(graph, info.metadata)

    # 3. Generate deterministic queries
    queries = generate_benchmark_queries(graph, count=10, seed=42, objective="distance")
    print(f"Generated {len(queries)} reachable benchmark query pairs.")

    # 4, 5, 6. Run Dijkstra, A*, and Bidirectional Dijkstra
    test_q = queries[0]
    res_dijkstra = dijkstra(graph, test_q.source, test_q.target, objective="distance")
    res_astar = astar(graph, test_q.source, test_q.target, objective="distance")
    res_bi = bidirectional_dijkstra(graph, test_q.source, test_q.target, objective="distance")

    # 7 & 8. Compare route costs and verify against NetworkX oracle
    v_dijkstra = verify_route_correctness_and_optimality(
        graph, res_dijkstra, test_q.source, test_q.target, objective="distance"
    )
    v_astar = verify_route_correctness_and_optimality(
        graph, res_astar, test_q.source, test_q.target, objective="distance"
    )
    v_bi = verify_route_correctness_and_optimality(
        graph, res_bi, test_q.source, test_q.target, objective="distance"
    )

    costs_match = res_dijkstra.optimized_cost == res_astar.optimized_cost == res_bi.optimized_cost

    # 9 & 10. Measure runtimes and expanded nodes
    print(
        f"\nDijkstra:     Cost={res_dijkstra.optimized_cost:.1f} m, "
        f"Exp={res_dijkstra.nodes_expanded}, Exam={res_dijkstra.edges_examined}"
    )
    print(
        f"A*:           Cost={res_astar.optimized_cost:.1f} m, "
        f"Exp={res_astar.nodes_expanded}, Exam={res_astar.edges_examined}"
    )
    print(
        f"Bidirectional:Cost={res_bi.optimized_cost:.1f} m, "
        f"Exp={res_bi.nodes_expanded}, Exam={res_bi.edges_examined}"
    )

    # 11. Run memory profiling
    peak_bytes, peak_mb, _ = measure_peak_memory(
        dijkstra, graph, test_q.source, test_q.target, objective="distance"
    )
    print(f"Peak Python-tracked memory: {peak_mb:.4f} MB ({peak_bytes} bytes)")

    # 12, 13, 14. Full benchmark execution and export into temp directory
    with TemporaryDirectory() as tmp_dir:
        cfg = BenchmarkConfig(
            dataset_id="offline_sample",
            graph_sizes=[10, 14],
            algorithms=["dijkstra", "astar", "bidirectional_dijkstra"],
            objectives=["distance", "travel_time"],
            query_count=5,
            repetitions=2,
            warmup_runs=1,
            memory_enabled=True,
            correctness_enabled=True,
        )

        raw, summaries, comparisons, datasets_meta, manifest = run_benchmarks(graph, config=cfg)
        out_dir = export_benchmark_results(
            raw, summaries, comparisons, datasets_meta, manifest, output_directory=tmp_dir
        )
        loaded = load_benchmark_experiment(out_dir)

        exports_valid = (
            len(loaded["raw"]) > 0
            and len(loaded["summary"]) > 0
            and len(loaded["comparisons"]) > 0
            and len(loaded["correctness"]) > 0
            and loaded["manifest"]["experiment_id"] == manifest.experiment_id
        )

        all_summaries_optimal = all(s.optimality_verification_rate == 1.0 for s in summaries)
        all_summaries_valid = all(s.route_validity_rate == 1.0 for s in summaries)

    # 15. Verify original graph immutability
    immutability_passed = (
        dict(graph.nodes(data=True)) == nodes_snapshot
        and list(graph.edges(keys=True, data=True)) == edges_snapshot
    )

    # 16. Print PASS / FAIL checks
    checks = {
        "Graph validation": val_report.valid,
        "Query generation (deterministic & reachable)": len(queries) > 0,
        "Dijkstra optimality (NetworkX match)": v_dijkstra[1],
        "A* optimality (NetworkX match)": v_astar[1],
        "Bidirectional Dijkstra optimality (NetworkX match)": v_bi[1],
        "All algorithms produce identical optimal cost": costs_match,
        "Memory profiling execution": peak_bytes > 0 and peak_mb > 0.0,
        "Benchmark runner execution (multi-size, 3 algos, 2 objectives)": len(raw) > 0,
        "Summary aggregation (100% validity & optimality)": all_summaries_valid
        and all_summaries_optimal,
        "Paired comparisons calculation": len(comparisons) > 0,
        "CSV and JSON manifest export integrity": exports_valid,
        "Original graph immutability": immutability_passed,
    }

    print("\n" + "=" * 65)
    print("CHECKLIST RESULTS:")
    print("=" * 65)
    for label, status in checks.items():
        print(f"[{'PASS' if status else 'FAIL'}] {label}")

    all_passed = all(checks.values())
    print("=" * 65)
    print(f"PHASE 9 VERIFICATION: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 65)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
