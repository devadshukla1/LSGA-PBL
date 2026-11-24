"""Command-line interface runner for reproducible routing algorithm benchmarks."""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import (
    DEFAULT_BENCHMARK_PAIRS,
    DEFAULT_BENCHMARK_REPETITIONS,
    DEFAULT_RANDOM_SEED,
)
from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.benchmark_runner import run_benchmarks
from src.benchmarks.report_export import export_benchmark_results
from src.graph.dataset_service import load


def main() -> int:
    parser = argparse.ArgumentParser(description="Run routing algorithm benchmarks.")
    parser.add_argument(
        "--dataset", default="offline_sample", help="Dataset identifier or 'offline'"
    )
    parser.add_argument(
        "--pairs", type=int, default=DEFAULT_BENCHMARK_PAIRS, help="Number of query pairs"
    )
    parser.add_argument(
        "--repetitions", type=int, default=DEFAULT_BENCHMARK_REPETITIONS, help="Repetitions"
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED, help="Random seed")
    parser.add_argument(
        "--objectives",
        nargs="+",
        default=["distance", "travel_time"],
        choices=["distance", "travel_time"],
        help="Objectives to benchmark",
    )
    parser.add_argument(
        "--algorithms",
        nargs="+",
        default=["dijkstra", "astar", "bidirectional_dijkstra"],
        choices=["dijkstra", "astar", "bidirectional_dijkstra"],
        help="Algorithms to benchmark",
    )
    parser.add_argument(
        "--memory", action="store_true", default=True, help="Enable memory profiling"
    )
    parser.add_argument("--output-dir", default=None, help="Output directory path")

    args = parser.parse_args()

    ds_name = (
        "offline_sample"
        if args.dataset in {"offline", "sample", "offline_sample"}
        else args.dataset
    )
    info = load(ds_name)
    graph = info.graph

    print("=" * 65)
    print("SMART CITY TRAFFIC & EMERGENCY ROUTE OPTIMIZER")
    print("BENCHMARK RUNNER · PHASE 9")
    print("=" * 65)
    print(
        f"Target Dataset: {info.metadata.dataset_name} "
        f"({len(graph)} nodes, {graph.number_of_edges()} edges)"
    )
    print(f"Algorithms:     {', '.join(args.algorithms)}")
    print(f"Objectives:     {', '.join(args.objectives)}")
    print(f"Query Pairs:    {args.pairs}")
    print(f"Repetitions:    {args.repetitions}")
    print(f"Random Seed:    {args.seed}")
    print(f"Memory Mode:    {'Enabled' if args.memory else 'Disabled'}")

    max_size = len(graph)
    target_sizes = [s for s in [50, 100, 500, 1000] if s < max_size]

    cfg = BenchmarkConfig(
        dataset_id=ds_name,
        graph_sizes=target_sizes,
        algorithms=args.algorithms,
        objectives=args.objectives,
        query_count=args.pairs,
        repetitions=args.repetitions,
        random_seed=args.seed,
        warmup_runs=1,
        memory_enabled=args.memory,
        correctness_enabled=True,
    )

    def on_progress(step: int, total: int, msg: str) -> None:
        print(f"[{step}/{total}] {msg}")

    print("\nExecuting benchmark protocol...")
    raw, summaries, comparisons, datasets, manifest = run_benchmarks(
        graph, config=cfg, progress_callback=on_progress
    )

    out_dir = export_benchmark_results(
        raw, summaries, comparisons, datasets, manifest, output_directory=args.output_dir
    )

    print("\nBenchmark completed successfully.")
    print(f"Results exported to: {out_dir}")

    # Summary table
    print("\n" + "=" * 65)
    print("SUMMARY RESULTS:")
    print("=" * 65)
    for s in summaries:
        print(
            f"{s.algorithm:22} | {s.objective:11} | {s.graph_size_label:6} | "
            f"Mean: {s.mean_runtime_ms:7.3f} ms | Nodes: {s.mean_nodes_expanded:5.1f} | "
            f"Valid: {s.route_validity_rate * 100:5.1f}% | "
            f"Opt: {s.optimality_verification_rate * 100:5.1f}%"
        )

    # Correctness check
    all_valid = all(s.route_validity_rate == 1.0 for s in summaries)
    all_optimal = all(s.optimality_verification_rate == 1.0 for s in summaries)

    if not (all_valid and all_optimal):
        print("\n[CRITICAL ERROR] Route validity or optimality check failed!")
        return 1

    print("\n[PASS] All correctness and optimality verifications succeeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
