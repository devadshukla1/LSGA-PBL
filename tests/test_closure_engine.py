"""Unit and property tests for station closure engine and graph isolation."""

import networkx as nx
import pytest

from src.simulation.closure_engine import StationClosureError, simulate_station_closure


@pytest.fixture
def chain_graph():
    """A - B - C - D (Chain)."""
    mg = nx.MultiGraph()
    for s in ["A", "B", "C", "D"]:
        mg.add_node(s, station_name=f"Station {s}")
    mg.add_edge("A", "B", key="1", distance_km=1.0, estimated_time_min=2.0)
    mg.add_edge("B", "C", key="2", distance_km=1.0, estimated_time_min=2.0)
    mg.add_edge("C", "D", key="3", distance_km=1.0, estimated_time_min=2.0)
    return mg


@pytest.fixture
def parallel_line_graph():
    """A and B connected by two parallel line edges (L1 and L2). B connected to C."""
    mg = nx.MultiGraph()
    for s in ["A", "B", "C"]:
        mg.add_node(s, station_name=s)
    mg.add_edge("A", "B", key="p1", line_id="L1", distance_km=2.0, estimated_time_min=3.0)
    mg.add_edge("A", "B", key="p2", line_id="L2", distance_km=2.0, estimated_time_min=3.0)
    mg.add_edge("B", "C", key="p3", line_id="L1", distance_km=2.0, estimated_time_min=3.0)
    return mg


def test_single_station_closure_chain(chain_graph):
    """Closing B in A-B-C-D leaves A isolated and C-D connected (2 components)."""
    orig_nodes = chain_graph.number_of_nodes()
    orig_edges = chain_graph.number_of_edges()

    res = simulate_station_closure(chain_graph, closed_station_ids=["B"])

    # 1. Original graph must NOT be mutated
    assert chain_graph.number_of_nodes() == orig_nodes == 4
    assert chain_graph.number_of_edges() == orig_edges == 3
    assert chain_graph.has_node("B")

    # 2. Simulated graph checks
    sim_g = res.simulation_graph
    assert sim_g.number_of_nodes() == 3
    assert not sim_g.has_node("B")
    assert sim_g.has_node("A")
    assert sim_g.has_node("C")
    assert sim_g.has_node("D")
    assert sim_g.number_of_edges() == 1  # only C-D remains

    # 3. Disruption metrics
    assert res.removed_stations_count == 1
    assert res.removed_edges_count == 2
    assert res.post_closure_metrics.connected_components == 2
    assert res.post_closure_metrics.largest_component_size == 2  # {C, D}
    assert res.post_closure_metrics.isolated_stations_count == 1  # {A}


def test_multiple_station_closure(chain_graph):
    """Closing B and D leaves {A} and {C} as two isolated stations."""
    res = simulate_station_closure(chain_graph, closed_station_ids=["B", "D"])

    assert res.removed_stations_count == 2
    assert res.removed_edges_count == 3
    sim_g = res.simulation_graph
    assert sim_g.number_of_nodes() == 2
    assert sim_g.number_of_edges() == 0
    assert res.post_closure_metrics.isolated_stations_count == 2
    assert res.post_closure_metrics.connected_components == 2


def test_empty_closure_returns_baseline(chain_graph):
    """Empty list or None should return baseline graph stats with 0 removals."""
    res = simulate_station_closure(chain_graph, closed_station_ids=[])

    assert res.removed_stations_count == 0
    assert res.removed_edges_count == 0
    assert res.component_count_change == 0
    assert res.simulation_graph.number_of_nodes() == 4
    assert res.simulation_graph.number_of_edges() == 3


def test_parallel_edges_incident_removal(parallel_line_graph):
    """Closing A must cleanly remove both parallel edges (A, B, p1) and (A, B, p2)."""
    res = simulate_station_closure(parallel_line_graph, closed_station_ids=["A"])

    sim_g = res.simulation_graph
    assert sim_g.number_of_nodes() == 2
    assert not sim_g.has_node("A")
    assert sim_g.number_of_edges() == 1  # Only (B, C, p3) remains
    assert sim_g.has_edge("B", "C")


def test_unknown_station_raises_error(chain_graph):
    """Closing a non-existent station ID must raise StationClosureError."""
    with pytest.raises(StationClosureError):
        simulate_station_closure(chain_graph, closed_station_ids=["NON_EXISTENT"])
