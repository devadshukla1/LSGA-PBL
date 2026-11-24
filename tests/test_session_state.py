"""Tests for session state management and dataset fingerprinting."""

import streamlit as st

from src.core.settings import SAMPLE_DATA_DIR
from src.ui.session_state import (
    DEFAULT_SESSION_STATE,
    get_cached_dataset_bundle,
    get_cached_graph_bundle,
    init_session_state,
    invalidate_stale_results,
)


def test_session_state_initialization():
    """Verify default session state values are correctly assigned."""
    init_session_state()
    for key in DEFAULT_SESSION_STATE:
        assert key in st.session_state


def test_invalidate_stale_results():
    """Verify that fingerprint changes wipe dependent route and closure states."""
    st.session_state["dataset_fingerprint"] = "old_fp"
    st.session_state["route_result"] = "mock_route"
    st.session_state["comparison_df"] = "mock_comp"
    st.session_state["closed_stations"] = ["STN1"]
    st.session_state["closure_result"] = "mock_closure"

    invalidate_stale_results("new_fp")

    assert st.session_state["dataset_fingerprint"] == "new_fp"
    assert st.session_state["route_result"] is None
    assert st.session_state["comparison_df"] is None
    assert st.session_state["closed_stations"] == []
    assert st.session_state["closure_result"] is None


def test_caching_immutable_graph():
    """Verify that get_cached_graph_bundle creates and returns valid MultiGraph."""
    stations_df, lines_df, connections_df, station_lines_df, metadata = get_cached_dataset_bundle(str(SAMPLE_DATA_DIR))
    fp = metadata.get("fingerprint", "sample_test_fp")

    graph, validation = get_cached_graph_bundle(fp, stations_df, lines_df, connections_df, station_lines_df)
    assert graph.number_of_nodes() == 12
    assert validation["node_count"] == 12
