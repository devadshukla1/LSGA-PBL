"""Tests for session state synchronization and cache invalidation helpers."""

import streamlit as st

from src.ui.state import (
    ensure_session_state,
    get_active_dataset_id,
    invalidate_dataset_state,
    set_active_dataset_id,
)


def test_ensure_session_state() -> None:
    """Verify session state defaults are populated if missing."""
    st.session_state.clear()
    ensure_session_state()
    assert st.session_state["active_dataset_id"] == "sample_network"
    assert st.session_state["selected"] == "sample_network"
    assert st.session_state["route_output"] is None
    assert st.session_state["sim_output"] is None


def test_get_and_set_active_dataset_id() -> None:
    """Verify active dataset retrieval and mutation with cache invalidation."""
    st.session_state.clear()
    ensure_session_state()

    assert get_active_dataset_id() == "sample_network"

    # Populate dummy computed outputs
    st.session_state["route_output"] = ("sample", "dummy_route", None)
    st.session_state["sim_output"] = ("sample", "dummy_sim", None)

    # Change dataset -> should invalidate computed outputs
    changed = set_active_dataset_id("offline_sample")
    assert changed is True
    assert get_active_dataset_id() == "offline_sample"
    assert "route_output" not in st.session_state
    assert "sim_output" not in st.session_state

    # Same dataset -> should return False without clearing
    st.session_state["route_output"] = "new_route"
    assert set_active_dataset_id("offline_sample") is False
    assert st.session_state.get("route_output") == "new_route"


def test_invalidate_dataset_state_with_keep() -> None:
    """Verify invalidation respects preserve keys."""
    st.session_state.clear()
    st.session_state["route_output"] = "keep_me"
    st.session_state["sim_output"] = "clear_me"

    invalidate_dataset_state(keep_keys={"route_output"})
    assert st.session_state.get("route_output") == "keep_me"
    assert "sim_output" not in st.session_state
