"""Unit tests for critical station impact analysis and vulnerability ranking."""

import networkx as nx

from src.simulation.critical_station_impact import (
    compute_all_stations_impact_ranking,
    evaluate_single_station_impact,
)


def test_star_center_impact():
    """In a star graph, removing center disconnects all leaves."""
    g = nx.MultiGraph()
    g.add_node("C", station_name="Center")
    for i in range(1, 5):
        g.add_node(f"L{i}", station_name=f"Leaf {i}")
        g.add_edge("C", f"L{i}", key=f"e{i}")

    impact = evaluate_single_station_impact(g, "C")
    assert impact["is_articulation_point"] is True
    assert impact["component_count_increase"] == 3  # 1 -> 4 components (increase of 3)
    assert impact["isolated_stations_created"] == 4  # all 4 leaves become isolated
    assert impact["reachable_pairs_loss"] == 10  # from 5*4/2 = 10 to 0


def test_leaf_impact_does_not_fragment():
    """In a star graph, removing a leaf does not fragment the remaining nodes."""
    g = nx.MultiGraph()
    g.add_node("C", station_name="Center")
    for i in range(1, 5):
        g.add_node(f"L{i}", station_name=f"Leaf {i}")
        g.add_edge("C", f"L{i}", key=f"e{i}")

    impact = evaluate_single_station_impact(g, "L1")
    assert impact["is_articulation_point"] is False
    assert impact["component_count_increase"] == 0
    assert impact["isolated_stations_created"] == 0


def test_all_stations_impact_ranking():
    g = nx.MultiGraph()
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "D")

    df = compute_all_stations_impact_ranking(g)
    assert len(df) == 4
    # Cut vertices B and C should top the ranking over endpoints A and D
    top_stations = set(df.iloc[:2]["Station ID"])
    assert top_stations == {"B", "C"}
