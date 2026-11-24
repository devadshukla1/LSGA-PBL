"""Unit tests for automatic route recalculation and detour evaluation."""

import networkx as nx
import pytest

from src.simulation.closure_engine import simulate_station_closure
from src.simulation.route_rerouting import compare_routes_across_closure


@pytest.fixture
def detour_network():
    """Graph with two routes between S and D:

    Path 1 (Primary, Fast): S -[L1]-> X -[L1]-> D (2 hops, 4 min)
    Path 2 (Alternative Detour): S -[L2]-> Y -[L2]-> Z -[L2]-> D (3 hops, 9 min)
    """
    g = nx.MultiGraph()
    for s in ["S", "D", "X", "Y", "Z"]:
        g.add_node(s, station_name=s)

    # Fast path via X
    g.add_edge("S", "X", key="e1", line_id="L1", distance_km=2.0, estimated_time_min=2.0)
    g.add_edge("X", "D", key="e2", line_id="L1", distance_km=2.0, estimated_time_min=2.0)

    # Detour path via Y and Z
    g.add_edge("S", "Y", key="d1", line_id="L2", distance_km=3.0, estimated_time_min=3.0)
    g.add_edge("Y", "Z", key="d2", line_id="L2", distance_km=3.0, estimated_time_min=3.0)
    g.add_edge("Z", "D", key="d3", line_id="L2", distance_km=3.0, estimated_time_min=3.0)
    return g


def test_reroute_succeeds_when_alternative_exists(detour_network):
    """Closing station X should force the routing engine to detour via Y and Z."""
    sim_res = simulate_station_closure(detour_network, closed_station_ids=["X"])

    reroute_res = compare_routes_across_closure(
        original_graph=detour_network,
        simulated_graph=sim_res.simulation_graph,
        source="S",
        destination="D",
        closed_station_ids=["X"],
        objective="minimum_time",
    )

    assert reroute_res.disruption_status == "REROUTED"
    assert reroute_res.original_reachable is True
    assert reroute_res.new_reachable is True
    assert reroute_res.original_station_path == ["S", "X", "D"]
    assert reroute_res.new_station_path == ["S", "Y", "Z", "D"]
    assert reroute_res.original_stops == 2
    assert reroute_res.new_stops == 3
    assert reroute_res.stops_diff == 1
    assert reroute_res.time_diff_min == 5.0  # 9 min - 4 min


def test_route_unreachable_when_critical_station_closed(detour_network):
    """Closing both X and Y severs all possible paths between S and D."""
    sim_res = simulate_station_closure(detour_network, closed_station_ids=["X", "Y"])

    reroute_res = compare_routes_across_closure(
        original_graph=detour_network,
        simulated_graph=sim_res.simulation_graph,
        source="S",
        destination="D",
        closed_station_ids=["X", "Y"],
        objective="minimum_time",
    )

    assert reroute_res.disruption_status == "UNREACHABLE"
    assert reroute_res.original_reachable is True
    assert reroute_res.new_reachable is False
    assert "severed" in reroute_res.message.lower()


def test_endpoint_closed_handling(detour_network):
    """When the destination station D itself is closed, status must be ENDPOINT_CLOSED."""
    sim_res = simulate_station_closure(detour_network, closed_station_ids=["D"])

    reroute_res = compare_routes_across_closure(
        original_graph=detour_network,
        simulated_graph=sim_res.simulation_graph,
        source="S",
        destination="D",
        closed_station_ids=["D"],
        objective="minimum_time",
    )

    assert reroute_res.disruption_status == "ENDPOINT_CLOSED"
    assert reroute_res.new_reachable is False


def test_unchanged_route_when_unrelated_station_closed(detour_network):
    """Closing station Y does not affect the optimal primary path via X."""
    sim_res = simulate_station_closure(detour_network, closed_station_ids=["Y"])

    reroute_res = compare_routes_across_closure(
        original_graph=detour_network,
        simulated_graph=sim_res.simulation_graph,
        source="S",
        destination="D",
        closed_station_ids=["Y"],
        objective="minimum_time",
    )

    assert reroute_res.disruption_status == "UNCHANGED"
    assert reroute_res.new_station_path == ["S", "X", "D"]
    assert reroute_res.stops_diff == 0
    assert reroute_res.time_diff_min == 0.0
