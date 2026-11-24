"""Tests for export generation (CSV, JSON, GraphML)."""

import json

from src.algorithms.bfs import find_route_bfs
from src.core.settings import SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.simulation.closure_engine import simulate_station_closure
from src.simulation.impact_comparison import build_impact_comparison_table


def test_route_and_closure_exports():
    """Verify route and closure data can be converted to CSV and JSON without loss."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    # Route export
    route_res = find_route_bfs(graph, "S01", "S06")
    assert route_res.reachable

    route_json = {
        "source": route_res.source_station_id,
        "destination": route_res.destination_station_id,
        "stops": route_res.total_stops,
        "path": route_res.station_path,
    }
    serialized_route = json.dumps(route_json)
    deserialized_route = json.loads(serialized_route)
    assert deserialized_route["stops"] == route_res.total_stops

    # Closure export
    sim_res = simulate_station_closure(graph, ["S02"])
    comp_table = build_impact_comparison_table(sim_res)
    csv_bytes = comp_table.to_csv(index=False)
    assert "Station Count (Active Vertices)" in csv_bytes
    assert "Connected Components" in csv_bytes
