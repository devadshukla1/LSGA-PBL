"""Master reproduction orchestrator for MetroGraph Analytics.

Validates datasets, executes routing experiments, computes station importance,
simulates resilience outages, and optionally runs performance benchmarks.
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_resilience_experiments import run_resilience_experiments
from scripts.run_route_experiments import run_route_experiments
from scripts.run_station_analysis import run_station_analysis
from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.graph.validator import validate_metro_graph


def reproduce_all(dataset_mode: str = "metro", run_benchmarks_flag: bool = False):
    print("=" * 80)
    print("METROGRAPH ANALYTICS - FULL RESULTS REPRODUCTION PIPELINE")
    print(f"Dataset Mode: {dataset_mode.upper()} | Include Benchmarks: {run_benchmarks_flag}")
    print("=" * 80)

    # 1. Dataset Validation & Graph Construction
    data_dir = METRO_DATA_DIR if dataset_mode == "metro" else SAMPLE_DATA_DIR
    print(f"\n[STEP 1/5] Validating dataset and constructing graph from {data_dir.name}...")
    stations_df, lines_df, connections_df, station_lines_df, metadata = load_validated_dataset(data_dir)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)
    validation = validate_metro_graph(graph)
    print(
        f"  Topology Verified: {validation['node_count']} stations, "
        f"{validation['edge_count']} connections, {validation['interchange_station_count']} interchanges."
    )

    # 2. Multi-Objective Route Comparison Experiments
    print("\n[STEP 2/5] Running multi-objective route comparison experiments...")
    route_df = run_route_experiments(dataset_mode)
    print(f"  Generated {len(route_df)} route evaluation records.")

    # 3. Station Importance & Centrality Rankings
    print("\n[STEP 3/5] Computing station importance, centralities & articulation points...")
    station_df = run_station_analysis(dataset_mode)
    print(f"  Computed structural metrics for {len(station_df)} stations.")

    # 4. Resilience & Outage Simulations
    print("\n[STEP 4/5] Executing network resilience closure scenarios...")
    resilience_df = run_resilience_experiments(dataset_mode)
    print(f"  Evaluated {len(resilience_df)} disruption scenarios.")

    # 5. Optional Benchmarks
    if run_benchmarks_flag:
        print("\n[STEP 5/5] Running microbenchmarking suite...")
        from scripts.benchmark_algorithms import run_benchmarks
        run_benchmarks(repetitions=10)
    else:
        print("\n[STEP 5/5] Skipping microbenchmarks (run with --benchmarks to execute).")

    print("\n" + "=" * 80)
    print("ALL EXPERIMENTAL ARTIFACTS REPRODUCED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce all MetroGraph Analytics experimental results.")
    parser.add_argument("--dataset", choices=["sample", "metro"], default="sample", help="Target dataset mode")
    parser.add_argument("--benchmarks", action="store_true", help="Include performance microbenchmarking")
    args = parser.parse_args()
    reproduce_all(args.dataset, args.benchmarks)
