"""Tests for station importance ranking pipeline."""

import networkx as nx
import pandas as pd
import pytest

from src.analytics.models import StationAnalyticsResult
from src.analytics.station_ranking import compute_station_analytics, get_ranked_stations_dataframe


@pytest.fixture
def sample_multigraph():
    mg = nx.MultiGraph()
    mg.add_node("S1", station_name="Central", lines={"L1", "L2"}, is_interchange=True)
    mg.add_node("S2", station_name="North", lines={"L1"}, is_interchange=False)
    mg.add_node("S3", station_name="South", lines={"L2"}, is_interchange=False)

    mg.add_edge("S1", "S2", key="e1", line_id="L1", distance_km=2.0, estimated_time_min=3.0)
    mg.add_edge("S1", "S3", key="e2", line_id="L2", distance_km=3.0, estimated_time_min=4.0)
    return mg


def test_compute_station_analytics(sample_multigraph):
    sl_df = pd.DataFrame([
        {"station_id": "S1", "line_id": "L1"},
        {"station_id": "S1", "line_id": "L2"},
        {"station_id": "S2", "line_id": "L1"},
        {"station_id": "S3", "line_id": "L2"},
    ])
    l_df = pd.DataFrame([
        {"line_id": "L1", "line_name": "Line 1"},
        {"line_id": "L2", "line_name": "Line 2"},
    ])

    results, summary, sg = compute_station_analytics(sample_multigraph, sl_df, l_df)

    assert len(results) == 3
    assert summary.total_stations == 3
    assert summary.total_connections == 2
    assert summary.total_interchanges == 1
    assert summary.total_articulation_points == 1  # S1 is articulation point

    res_map = {r.station_id: r for r in results}
    assert res_map["S1"].is_interchange is True
    assert res_map["S1"].is_articulation_point is True
    assert res_map["S1"].degree == 2
    assert res_map["S1"].betweenness_centrality == 1.0


def test_get_ranked_stations_dataframe():
    dummy_results = [
        StationAnalyticsResult(
            station_id="A",
            station_name="Alpha",
            degree=2,
            degree_centrality=0.5,
            betweenness_centrality=0.1,
            line_count=1,
            line_names=["Red"],
        ),
        StationAnalyticsResult(
            station_id="B",
            station_name="Beta",
            degree=4,
            degree_centrality=1.0,
            betweenness_centrality=0.8,
            line_count=2,
            line_names=["Red", "Blue"],
            is_interchange=True,
            is_articulation_point=True,
        ),
    ]

    df_ranked = get_ranked_stations_dataframe(dummy_results, sort_by="betweenness_centrality", top_n=10)
    assert len(df_ranked) == 2
    assert df_ranked.iloc[0]["Station ID"] == "B"
    assert df_ranked.iloc[0]["Rank"] == 1
    assert df_ranked.iloc[1]["Station ID"] == "A"
    assert df_ranked.iloc[1]["Rank"] == 2
