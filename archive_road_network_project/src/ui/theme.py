"""Consistent modern dark-slate aesthetic theme and styling tokens for SmartRoute Analytics."""

from typing import Final

import streamlit as st

COLOR_PALETTE: Final[dict[str, str]] = {
    "bg_dark": "#0B1120",
    "card_bg": "#111827",
    "card_border": "#1E293B",
    "primary_sky": "#38BDF8",
    "accent_blue": "#2563EB",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "success_green": "#22C55E",
    "warning_amber": "#F59E0B",
    "error_red": "#EF4444",
}

CUSTOM_CSS: Final[str] = """
<style>
/* SmartRoute Analytics Dark Theme Styling */
.main-header-title {
    font-size: 2.1rem;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}

.main-header-subtitle {
    font-size: 0.95rem;
    font-weight: 400;
    color: #94A3B8;
    margin-bottom: 1rem;
}

.metric-card-container {
    background: #111827;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.metric-card-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94A3B8;
    margin-bottom: 4px;
}

.metric-card-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #38BDF8;
    line-height: 1.2;
}

.metric-card-delta {
    font-size: 0.8rem;
    font-weight: 500;
    margin-top: 4px;
}

.badge-pill {
    display: inline-block;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 9999px;
    text-transform: uppercase;
}

.badge-success {
    background-color: rgba(34, 197, 94, 0.15);
    color: #22C55E;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-warning {
    background-color: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-info {
    background-color: rgba(56, 189, 248, 0.15);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.3);
}

.empty-state-box {
    background: #111827;
    border: 1px dashed #334155;
    border-radius: 8px;
    padding: 32px 20px;
    text-align: center;
    color: #94A3B8;
}

.section-divider {
    border-top: 1px solid #1E293B;
    margin: 20px 0;
}
</style>
"""


def inject_custom_theme() -> None:
    """Inject custom responsive dark-slate CSS into Streamlit page context."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
