"""Session state management and dataset fingerprinting for MetroGraph Analytics."""

from typing import Any, Dict

import pandas as pd
import streamlit as st

from src.data.loader import (
    load_validated_dataset,
)
from src.graph.metro_builder import build_metro_graph
from src.graph.validator import validate_metro_graph
from src.ui.sidebar import get_active_dataset_directory

DEFAULT_SESSION_STATE: Dict[str, Any] = {
    "selected_dataset_mode": "delhi_metro",
    "dataset_fingerprint": "",
    "selected_source": None,
    "selected_destination": None,
    "routing_objective": "Minimum Transfers (0-1 BFS)",
    "transfer_penalty_minutes": 5.0,
    "route_result": None,
    "comparison_df": None,
    "closed_stations": [],
    "closure_result": None,
    "reroute_result": None,
    "analytics_preferences": {
        "top_n": 20,
        "ranking_metric": "Betweenness Centrality",
        "viz_metric": "Betweenness Centrality",
    },
}


def init_session_state() -> None:
    """Initializes global session state keys with safe defaults if not already set."""
    for key, default_val in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = default_val


def invalidate_stale_results(new_fingerprint: str) -> None:
    """Clears cached computation results when dataset fingerprint changes."""
    if st.session_state.get("dataset_fingerprint") != new_fingerprint:
        st.session_state["dataset_fingerprint"] = new_fingerprint
        st.session_state["route_result"] = None
        st.session_state["comparison_df"] = None
        st.session_state["closed_stations"] = []
        st.session_state["closure_result"] = None
        st.session_state["reroute_result"] = None
        st.session_state["selected_source"] = None
        st.session_state["selected_destination"] = None


@st.cache_data(show_spinner=False)
def get_cached_dataset_bundle(dir_path: str):
    """Loads and validates dataset from directory path using Streamlit caching.

    Returns:
        Tuple of (stations_df, lines_df, connections_df, station_lines_df, metadata)
    """
    return load_validated_dataset(dir_path)


@st.cache_resource(show_spinner=False)
def get_cached_graph_bundle(fp: str, _stations_df: pd.DataFrame, _lines_df: pd.DataFrame,
                            _connections_df: pd.DataFrame, _station_lines_df: pd.DataFrame):
    """Builds and validates the NetworkX MultiGraph from dataframes.

    Uses fingerprint as primary cache key. Does not mutate the graph.

    Returns:
        Tuple of (metro_graph, validation_dict)
    """
    graph = build_metro_graph(_stations_df, _lines_df, _connections_df, _station_lines_df)
    validation = validate_metro_graph(graph)
    return graph, validation


def get_current_dataset_and_graph():
    """High-level helper to fetch active dataset dataframes, metadata, and graph.

    Automatically syncs session state, checks fingerprint, and invalidates stale state.

    Returns:
        Tuple of (stations_df, lines_df, connections_df, station_lines_df, metadata, metro_graph, validation)
    """
    init_session_state()
    dataset_mode = st.session_state.get("selected_dataset_mode", "delhi_metro")
    active_dir = get_active_dataset_directory(dataset_mode)

    stations_df, lines_df, connections_df, station_lines_df, metadata = get_cached_dataset_bundle(str(active_dir))
    fp = metadata.get("fingerprint", "default_fp")

    invalidate_stale_results(fp)

    metro_graph, validation = get_cached_graph_bundle(
        fp, stations_df, lines_df, connections_df, station_lines_df
    )

    return stations_df, lines_df, connections_df, station_lines_df, metadata, metro_graph, validation
