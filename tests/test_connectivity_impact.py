"""Unit tests for topological connectivity impact and reachability metrics."""

import networkx as nx

from src.simulation.connectivity_impact import compute_connectivity_metrics


def test_reachability_metrics_complete_graph():
    """In a connected graph of N=5 nodes, reachable pairs = 5*4/2 = 10, ratio = 1.0."""
    g = nx.MultiGraph(nx.complete_graph(5))
    metrics = compute_connectivity_metrics(g)

    assert metrics.station_count == 5
    assert metrics.connected_components == 1
    assert metrics.is_connected is True
    assert metrics.reachable_station_pairs == 10
    assert metrics.possible_station_pairs == 10
    assert metrics.reachability_ratio == 1.0


def test_reachability_metrics_disconnected_components():
    """Two components of size 3 and 2:

    Possible pairs for N=5: 5*4/2 = 10.
    Component 1 (size 3): 3*2/2 = 3 pairs.
    Component 2 (size 2): 2*1/2 = 1 pair.
    Total reachable pairs = 4.
    Reachability ratio = 4 / 10 = 0.4.
    """
    g = nx.MultiGraph()
    # Comp 1: A-B-C
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    # Comp 2: D-E
    g.add_edge("D", "E")

    metrics = compute_connectivity_metrics(g)
    assert metrics.station_count == 5
    assert metrics.connected_components == 2
    assert metrics.is_connected is False
    assert metrics.largest_component_size == 3
    assert metrics.smallest_component_size == 2
    assert metrics.reachable_station_pairs == 4
    assert metrics.possible_station_pairs == 10
    assert metrics.reachability_ratio == 0.4


def test_reachability_isolated_nodes():
    """4 completely isolated nodes: reachable pairs = 0, ratio = 0.0."""
    g = nx.MultiGraph()
    g.add_nodes_from(["1", "2", "3", "4"])

    metrics = compute_connectivity_metrics(g)
    assert metrics.station_count == 4
    assert metrics.edge_count == 0
    assert metrics.connected_components == 4
    assert metrics.isolated_stations_count == 4
    assert metrics.reachable_station_pairs == 0
    assert metrics.reachability_ratio == 0.0


def test_reachability_empty_graph():
    g = nx.MultiGraph()
    metrics = compute_connectivity_metrics(g)
    assert metrics.station_count == 0
    assert metrics.connected_components == 0
    assert metrics.reachable_station_pairs == 0
