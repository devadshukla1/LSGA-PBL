"""Sidebar dataset status and branding panel for MetroGraph Analytics."""

import streamlit as st

from src.core.settings import (
    APP_ICON,
    APP_NAME,
    APP_TITLE,
    METRO_DATA_DIR,
    SAMPLE_DATA_DIR,
)
from src.data.loader import is_metro_dataset_available


def render_sidebar() -> str:
    """Renders the clean sidebar with branding and active Delhi Metro dataset status.

    Returns:
        The active dataset identifier: always 'delhi_metro' in production.
    """
    real_available = is_metro_dataset_available()
    dataset_mode = "delhi_metro"
    st.session_state["selected_dataset_mode"] = dataset_mode

    with st.sidebar:
        st.markdown(f"### {APP_ICON} {APP_NAME}")
        st.caption(APP_TITLE)
        st.divider()

        st.markdown("#### 📂 Active Dataset")
        st.markdown("**Delhi Metro Network (Real NCR)**")

        if real_available:
            st.success("🟢 Delhi Metro: Loaded & Verified")
            st.caption("260 Stations • 13 Metro Lines • 25 Interchanges")
        else:
            st.error("🔴 Delhi Metro Dataset Unavailable")
            st.caption("Missing or corrupted data files in data/metro/")

    return dataset_mode


def get_active_dataset_directory(dataset_mode: str = "delhi_metro"):
    """Resolves data directory path for Delhi Metro production dataset.

    Falls back to SAMPLE_DATA_DIR only if automated test suites pass an explicit 'synthetic' mode.
    """
    if dataset_mode == "delhi_metro":
        if is_metro_dataset_available():
            return METRO_DATA_DIR
        raise FileNotFoundError("Delhi Metro dataset is missing or unavailable in data/metro/")
    return SAMPLE_DATA_DIR
