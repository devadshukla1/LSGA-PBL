"""Station importance and topological centrality experiment runner.

Saves: results/experiments/station_importance.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics.station_ranking import compute_station_analytics, get_ranked_stations_dataframe
from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
from src.data.loader import is_metro_dataset_available, load_validated_dataset
from src.graph.metro_builder import build_metro_graph


def run_station_analysis(dataset_mode: str = "metro", output_csv: Path | None = None) -> pd.DataFrame:
    if dataset_mode == "metro" and is_metro_dataset_available():
        data_dir = METRO_DATA_DIR
    else:
        data_dir = SAMPLE_DATA_DIR

    stations_df, lines_df, connections_df, station_lines_df, metadata = load_validated_dataset(data_dir)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    print(f"Computing station importance on: {metadata.get('dataset_name', dataset_mode)}")
    station_results, summary, _ = compute_station_analytics(graph, station_lines_df, lines_df)
    ranked_df = get_ranked_stations_dataframe(station_results, sort_by="betweenness_centrality", top_n=None)

    if output_csv is None:
        output_csv = PROJECT_ROOT / "results" / "experiments" / "station_importance.csv"
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    ranked_df.to_csv(output_csv, index=False)
    print(f"[SUCCESS] Station importance rankings saved to: {output_csv}")

    # Top 10 Charts
    top10_bc = ranked_df.head(10)
    fig_bc = px.bar(
        top10_bc,
        x="Station Name",
        y="Betweenness Centrality",
        title=f"Top 10 Betweenness Centrality Stations ({metadata.get('dataset_name', '')})",
        color="Betweenness Centrality",
        color_continuous_scale="Viridis",
    )
    chart_path = PROJECT_ROOT / "results" / "reports" / "top10_betweenness.html"
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    fig_bc.write_html(str(chart_path))
    print(f"[SUCCESS] Top 10 betweenness chart saved to: {chart_path}")

    return ranked_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run station importance experiments.")
    parser.add_argument("--dataset", choices=["sample", "metro"], default="metro", help="Dataset mode")
    args = parser.parse_args()
    run_station_analysis(args.dataset)
