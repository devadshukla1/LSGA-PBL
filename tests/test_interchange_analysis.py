"""Tests for interchange station structural analysis."""

import networkx as nx
import pandas as pd

from src.analytics.interchange_analysis import analyze_interchange_stations


def test_interchange_detection():
    g = nx.Graph()
    for s in ["S1", "S2", "S3"]:
        g.add_node(s, station_name=s)

    sl_data = [
        {"station_id": "S1", "line_id": "L1"},
        {"station_id": "S2", "line_id": "L1"},
        {"station_id": "S2", "line_id": "L2"},  # S2 is interchange
        {"station_id": "S3", "line_id": "L2"},
    ]
    sl_df = pd.DataFrame(sl_data)

    lines_df = pd.DataFrame([
        {"line_id": "L1", "line_name": "Line 1"},
        {"line_id": "L2", "line_name": "Line 2"},
    ])

    res = analyze_interchange_stations(g, sl_df, lines_df)
    assert res["interchange_count"] == 1
    assert "S2" in res["interchange_station_ids"]
    assert "S1" not in res["interchange_station_ids"]
    assert "S3" not in res["interchange_station_ids"]

    details_df = res["interchange_details"]
    assert len(details_df) == 1
    assert details_df.iloc[0]["station_id"] == "S2"
    assert details_df.iloc[0]["line_count"] == 2
    assert "Line 1" in details_df.iloc[0]["line_names"]
    assert "Line 2" in details_df.iloc[0]["line_names"]
