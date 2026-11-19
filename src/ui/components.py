"""Reusable layout and visual components for SmartRoute Analytics pages."""

import streamlit as st


def render_page_header(
    title: str,
    subtitle: str | None = None,
    badge_phase: str | None = None,
) -> None:
    """Render a standardized page title banner with optional subtitle and phase badge."""
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    if badge_phase:
        st.info(badge_phase)


def render_section_header(title: str, caption: str | None = None) -> None:
    """Render a clean section header with optional clarifying caption."""
    st.subheader(title)
    if caption:
        st.caption(caption)


def render_metric_card(
    label: str,
    value: str,
    delta: str | None = None,
) -> None:
    """Render a key performance metric card with label, prominent value, and delta."""
    st.metric(label=label, value=value, delta=delta)


def render_badge(label: str, kind: str = "info") -> None:
    """Render a small colored status badge pill."""
    css_class = f"badge-{kind}" if kind in ("success", "warning", "info") else "badge-info"
    badge_html = f'<span class="badge-pill {css_class}">{label}</span>'
    st.markdown(badge_html, unsafe_allow_html=True)


def render_empty_state(
    message: str,
    hint: str | None = None,
) -> None:
    """Render an informative placeholder for empty or uncalculated views."""
    hint_html = f'<p style="font-size: 0.85rem; margin-top: 6px;">{hint}</p>' if hint else ""
    html = f"""
    <div class="empty-state-box">
        <p style="font-size: 1.05rem; font-weight: 500; margin: 0;">{message}</p>
        {hint_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
