"""Multi-objective route comparison experiment runner.

Saves: results/experiments/route_comparison.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.comparison import compare_routing_algorithms
from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
from src.data.loader import is_metro_dataset_available, load_validated_dataset
from src.graph.metro_builder import build_metro_graph


def run_route_experiments(dataset_mode: str = "metro", output_csv: Path | None = None) -> pd.DataFrame:
    if dataset_mode == "metro" and is_metro_dataset_available():
        data_dir = METRO_DATA_DIR
        pairs = [
            ("STN001", "STN026", "AIIMS to Cyber City"),
            ("STN199", "STN097", "Rajiv Chowk to Kashmere Gate"),
            ("STN053", "STN176", "Dwarka Sector 21 to Noida City Centre"),
            ("STN065", "STN101", "Hauz Khas to Kirti Nagar"),
        ]
    else:
        data_dir = SAMPLE_DATA_DIR
        pairs = [
            ("S01", "S06", "Central to Airport"),
            ("S03", "S09", "University to Tech Park"),
            ("S02", "S11", "North Market to South Hub"),
        ]

    stations_df, lines_df, connections_df, station_lines_df, metadata = load_validated_dataset(data_dir)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    all_records = []
    print(f"Running route experiments on: {metadata.get('dataset_name', dataset_mode)}")

    for src, dst, label in pairs:
        print(f"  Evaluating OD pair: {label} ({src} -> {dst})...")
        comp_df, _ = compare_routing_algorithms(graph, src, dst, transfer_penalty_min=5.0)
        for _, row in comp_df.iterrows():
            rec = row.to_dict()
            rec["Source_ID"] = src
            rec["Destination_ID"] = dst
            rec["OD_Pair_Label"] = label
            all_records.append(rec)

    results_df = pd.DataFrame(all_records)
    if output_csv is None:
        output_csv = PROJECT_ROOT / "results" / "experiments" / "route_comparison.csv"
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_csv, index=False)
    print(f"[SUCCESS] Route comparison experiments saved to: {output_csv}")
    return results_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run route comparison experiments.")
    parser.add_argument("--dataset", choices=["sample", "metro"], default="metro", help="Dataset mode")
    args = parser.parse_args()
    run_route_experiments(args.dataset)
