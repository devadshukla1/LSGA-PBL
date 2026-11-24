"""Resilience and station closure experiment runner.

Saves: results/experiments/closure_impact.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
from src.data.loader import is_metro_dataset_available, load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.simulation.closure_engine import simulate_station_closure
from src.simulation.route_rerouting import compare_routes_across_closure


def run_resilience_experiments(dataset_mode: str = "metro", output_csv: Path | None = None) -> pd.DataFrame:
    if dataset_mode == "metro" and is_metro_dataset_available():
        data_dir = METRO_DATA_DIR
        scenarios = [
            ("Baseline (No Closures)", [], "STN053", "STN176"),
            ("High Betweenness Hub (Rajiv Chowk)", ["STN199"], "STN053", "STN176"),
            ("Major Transfer Hub (Kashmere Gate)", ["STN097"], "STN199", "STN206"),
            ("Multi-Hub Severe Outage (Rajiv Chowk + Kashmere Gate)", ["STN199", "STN097"], "STN053", "STN176"),
            ("Cut-Vertex (Badarpur)", ["STN018"], "STN001", "STN018"),
        ]
    else:
        data_dir = SAMPLE_DATA_DIR
        scenarios = [
            ("Baseline (No Closures)", [], "S01", "S06"),
            ("Central Station Hub", ["S01"], "S03", "S06"),
            ("North Cut-Vertex Outage", ["S02"], "S01", "S03"),
            ("Double Station Outage", ["S01", "S04"], "S03", "S09"),
        ]

    stations_df, lines_df, connections_df, station_lines_df, metadata = load_validated_dataset(data_dir)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    rows = []
    print(f"Running resilience experiments on: {metadata.get('dataset_name', dataset_mode)}")

    for sc_name, closed_stns, src, dst in scenarios:
        print(f"  Simulating scenario: {sc_name}...")
        sim_res = simulate_station_closure(graph, closed_stns, dataset_id=metadata.get("dataset_name", ""))
        reroute_res = compare_routes_across_closure(
            original_graph=graph,
            simulated_graph=sim_res.simulation_graph,
            source=src,
            destination=dst,
            closed_station_ids=closed_stns,
            objective="Minimum Stops (BFS)",
        )
        p_m = sim_res.post_closure_metrics

        rows.append({
            "Scenario": sc_name,
            "Closed_Stations": ", ".join(closed_stns) if closed_stns else "None",
            "Closed_Count": len(closed_stns),
            "Remaining_Stations": p_m.station_count,
            "Remaining_Edges": p_m.edge_count,
            "Connected_Components": p_m.connected_components,
            "Largest_Component_Size": p_m.largest_component_size,
            "Reachable_Station_Pairs": p_m.reachable_station_pairs,
            "Reachable_Pairs_Lost": sim_res.reachable_pairs_loss,
            "Reachability_Ratio": round(p_m.reachability_ratio, 4),
            "Sample_Route_OD": f"{src} -> {dst}",
            "Reroute_Status": reroute_res.disruption_status,
            "Stops_Delta": reroute_res.stops_diff,
            "Time_Delta_Min": round(reroute_res.time_diff_min, 2),
        })

    res_df = pd.DataFrame(rows)
    if output_csv is None:
        output_csv = PROJECT_ROOT / "results" / "experiments" / "closure_impact.csv"
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(output_csv, index=False)
    print(f"[SUCCESS] Closure resilience experiments saved to: {output_csv}")
    return res_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run resilience closure experiments.")
    parser.add_argument("--dataset", choices=["sample", "metro"], default="metro", help="Dataset mode")
    args = parser.parse_args()
    run_resilience_experiments(args.dataset)
