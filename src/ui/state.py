"""Session state synchronization and cache invalidation helpers for Streamlit."""

from typing import Any

import streamlit as st

_STATE_DEFAULTS: dict[str, Any] = {
    "active_dataset_id": "sample_network",
    "selected": "sample_network",
    "route_output": None,
    "alternatives_output": None,
    "sim_output": None,
    "traversal_output": None,
    "structural_output": None,
    "partition_active_result": None,
    "active_benchmark_run": None,
}


def ensure_session_state() -> None:
    """Ensure standard application session state variables are initialized."""
    for key, default_val in _STATE_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_val


def get_active_dataset_id(fallback: str = "sample_network") -> str:
    """Return currently active dataset ID from session state."""
    return st.session_state.get("active_dataset_id") or st.session_state.get("selected") or fallback


def set_active_dataset_id(dataset_id: str) -> bool:
    """Set active dataset ID and invalidate downstream state if selection changed."""
    current = get_active_dataset_id()
    if current != dataset_id:
        st.session_state["active_dataset_id"] = dataset_id
        st.session_state["selected"] = dataset_id
        invalidate_dataset_state()
        return True
    return False


def invalidate_dataset_state(keep_keys: set[str] | None = None) -> None:
    """Purge dataset-dependent computed outputs from session state upon dataset switch."""
    keys_to_clear = [
        "route_output",
        "alternatives_output",
        "sim_output",
        "traversal_output",
        "structural_output",
        "partition_active_result",
        "dataset",
        "derived",
    ]
    keep = keep_keys or set()
    for key in keys_to_clear:
        if key not in keep and key in st.session_state:
            st.session_state.pop(key, None)
