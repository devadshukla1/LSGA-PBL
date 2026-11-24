"""Edge cases and boundary tests for station closure simulations."""

import networkx as nx

from src.simulation.closure_engine import simulate_station_closure
from src.simulation.impact_comparison import build_impact_comparison_table
from src.simulation.route_rerouting import compare_routes_across_closure


def test_close_all_stations():
    """Closing all stations in a graph leaves an empty graph."""
    g = nx.MultiGraph()
    g.add_edge("1", "2")

    res = simulate_station_closure(g, closed_station_ids=["1", "2"])
    assert res.post_closure_metrics.station_count == 0
    assert res.post_closure_metrics.edge_count == 0
    assert res.post_closure_metrics.reachable_station_pairs == 0
    assert res.post_closure_metrics.reachability_ratio == 0.0


def test_duplicate_station_ids_normalized():
    """Passing duplicate IDs like ['A', 'A', 'A'] should only remove station A once."""
    g = nx.MultiGraph()
    g.add_edge("A", "B")

    res = simulate_station_closure(g, closed_station_ids=["A", "A", "A"])
    assert res.removed_stations_count == 1
    assert res.closed_station_ids == ["A"]
    assert res.simulation_graph.number_of_nodes() == 1


def test_build_impact_comparison_table():
    g = nx.MultiGraph()
    g.add_edge("A", "B")
    g.add_edge("B", "C")

    res = simulate_station_closure(g, closed_station_ids=["B"])
    table_df = build_impact_comparison_table(res)

    assert not table_df.empty
    assert "Metric" in table_df.columns
    assert "Before Closure" in table_df.columns
    assert "After Closure" in table_df.columns
    assert "Change (Delta)" in table_df.columns


def test_route_across_disconnected_baseline():
    """Routing between two stations that were already disconnected before closure."""
    g = nx.MultiGraph()
    g.add_edge("A", "B", key="1", estimated_time_min=2.0, distance_km=1.0)
    g.add_edge("C", "D", key="2", estimated_time_min=2.0, distance_km=1.0)

    sim_res = simulate_station_closure(g, closed_station_ids=["A"])
    reroute_res = compare_routes_across_closure(
        original_graph=g,
        simulated_graph=sim_res.simulation_graph,
        source="B",
        destination="D",
        closed_station_ids=["A"],
    )

    assert reroute_res.disruption_status == "ALREADY_UNREACHABLE"
    assert reroute_res.original_reachable is False
    assert reroute_res.new_reachable is False
