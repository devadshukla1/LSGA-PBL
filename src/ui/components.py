"""Reusable UI presentation components and widgets for MetroGraph."""

from typing import Any, Optional

import streamlit as st

from src.ui.theme import THEME_COLORS


def render_page_header(title: str, subtitle: str, badge: str = "PHASE 7 INTEGRATED") -> None:
    """Renders a standard clean page header with title, subtitle, and phase badge."""
    col1, col2 = st.columns([0.82, 0.18])
    with col1:
        st.markdown(
            f"<h2 style='margin-bottom: 0px;' class='metro-title'>{title}</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p class='metro-subtitle'>{subtitle}</p>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div style='text-align: right; padding-top: 10px;'>"
            f"<span class='metro-badge'>{badge}</span></div>",
            unsafe_allow_html=True,
        )


def render_section_header(title: str, icon: str = "") -> None:
    """Renders a consistent section divider and heading."""
    prefix = f"{icon} " if icon else ""
    st.markdown(
        f"<div class='metro-section-title'>{prefix}{title}</div>",
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: Any, delta: Optional[str] = None) -> None:
    """Renders a styled metric card in dark theme."""
    delta_html = (
        f"<div style='color: {THEME_COLORS['success']}; font-size: 0.8rem; margin-top: 0.25rem; font-weight: 500;'>"
        f"{delta}</div>"
        if delta
        else ""
    )
    st.markdown(
        f"""
        <div class="metro-card" style="text-align: center;">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_box(title: str, message: str, level: str = "info") -> None:
    """Renders a styled notification box."""
    colors = {
        "info": THEME_COLORS["primary"],
        "success": THEME_COLORS["success"],
        "warning": THEME_COLORS["warning"],
        "error": THEME_COLORS["error"],
    }
    border_color = colors.get(level, THEME_COLORS["primary"])
    st.markdown(
        f"""
        <div style="border-left: 4px solid {border_color}; background-color: {THEME_COLORS['card_bg']}; """
        f"""padding: 0.9rem 1.1rem; border-radius: 6px; margin: 0.8rem 0; """
        f"""border: 1px solid {THEME_COLORS['card_border']};">
            <b style="color: {border_color}; font-size: 0.95rem;">{title}</b>
            <p style="color: {THEME_COLORS['text_muted']}; margin-top: 0.25rem; font-size: 0.9rem;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, message: str, icon: str = "🔍") -> None:
    """Renders a polished empty state placeholder."""
    st.markdown(
        f"""
        <div class="metro-empty-state">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-weight: 600; color: {THEME_COLORS['text_main']}; font-size: 1.05rem;">{title}</div>
            <div style="color: {THEME_COLORS['text_muted']}; font-size: 0.9rem; margin-top: 0.25rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dataset_status_card(metadata: dict, validation: dict) -> None:
    """Renders dataset metadata, source provenance, and invariants card."""
    d_name = metadata.get("dataset_name", "Metro Network")
    st.markdown(
        f"""
        <div class="metro-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <b style="color: {THEME_COLORS['primary']}; font-size: 1rem;">📂 {d_name}</b>
                <span class="metro-badge">v{metadata.get('version', '1.0')}</span>
            </div>
            <div style="color: {THEME_COLORS['text_muted']}; font-size: 0.85rem; line-height: 1.5;">
                <b>Source:</b> {metadata.get('source_organization', 'Open Archive')}<br/>
                <b>License:</b> {metadata.get('license', 'Open Data')} |
                <b>Coverage:</b> {metadata.get('geographic_coverage', 'NCR')} |
                <b>Fingerprint:</b> <code>{metadata.get('fingerprint', 'N/A')}</code><br/>
                <b>Topology:</b> {validation.get('node_count', 0)} stations, """
        f"""{validation.get('edge_count', 0)} connections, {validation.get('connected_components', 1)} component(s)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
