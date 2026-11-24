"""Tests for pairwise station comparison."""


from src.analytics.models import StationAnalyticsResult
from src.analytics.station_comparison import compare_two_stations


def test_compare_two_stations():
    results = [
        StationAnalyticsResult(
            station_id="S01",
            station_name="Central",
            degree=4,
            degree_centrality=0.8,
            betweenness_centrality=0.65,
            line_count=2,
            line_names=["Red", "Yellow"],
            is_interchange=True,
            is_articulation_point=False,
            component_id=1,
        ),
        StationAnalyticsResult(
            station_id="S02",
            station_name="Suburbs",
            degree=1,
            degree_centrality=0.2,
            betweenness_centrality=0.0,
            line_count=1,
            line_names=["Red"],
            is_interchange=False,
            is_articulation_point=False,
            component_id=1,
        ),
    ]

    cmp_df = compare_two_stations("S01", "S02", results)
    assert not cmp_df.empty
    assert "Station A" in cmp_df.columns
    assert "Station B" in cmp_df.columns
    assert "Attribute" in cmp_df.columns

    # Verify attributes
    attr_map = dict(zip(cmp_df["Attribute"], zip(cmp_df["Station A"], cmp_df["Station B"])))
    assert attr_map["Station Name"] == ("Central", "Suburbs")
    assert attr_map["Degree (Adjacent Stations)"] == ("4", "1")
    assert attr_map["Interchange Station?"] == ("Yes", "No")


def test_compare_identical_stations():
    results = [
        StationAnalyticsResult(
            station_id="S01",
            station_name="Central",
            degree=2,
            degree_centrality=0.4,
            betweenness_centrality=0.1,
            line_count=1,
            line_names=["Red"],
        ),
    ]

    cmp_df = compare_two_stations("S01", "S01", results)
    assert not cmp_df.empty
    attr_map = dict(zip(cmp_df["Attribute"], zip(cmp_df["Station A"], cmp_df["Station B"])))
    assert attr_map["Station Name"] == ("Central", "Central")
