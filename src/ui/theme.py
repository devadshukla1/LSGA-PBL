"""Design tokens and theme definition for MetroGraph UI."""

THEME_COLORS = {
    "background": "#0B1120",
    "sidebar": "#111827",
    "card_bg": "#1E293B",
    "card_border": "#334155",
    "primary": "#38BDF8",
    "primary_hover": "#0EA5E9",
    "secondary": "#818CF8",
    "text_main": "#F8FAFC",
    "text_muted": "#94A3B8",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "accent": "#818CF8",
}

CUSTOM_CSS = f"""
<style>
    /* Global container styling */
    .stApp {{
        background-color: {THEME_COLORS["background"]};
        color: {THEME_COLORS["text_main"]};
    }}

    /* Card container */
    .metro-card {{
        background-color: {THEME_COLORS["card_bg"]};
        border: 1px solid {THEME_COLORS["card_border"]};
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
    }}

    /* Header styling */
    .metro-title {{
        color: {THEME_COLORS["primary"]};
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    .metro-subtitle {{
        color: {THEME_COLORS["text_muted"]};
        font-size: 0.95rem;
        margin-bottom: 1.25rem;
    }}

    /* Section headers */
    .metro-section-title {{
        color: {THEME_COLORS["text_main"]};
        font-size: 1.2rem;
        font-weight: 600;
        border-bottom: 1px solid {THEME_COLORS["card_border"]};
        padding-bottom: 0.4rem;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }}

    /* Metric card */
    .metric-value {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {THEME_COLORS["primary"]};
        line-height: 1.2;
    }}
    .metric-label {{
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {THEME_COLORS["text_muted"]};
        margin-bottom: 0.25rem;
    }}

    /* Badge */
    .metro-badge {{
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #1E293B;
        color: {THEME_COLORS["primary"]};
        border: 1px solid #38BDF8;
    }}

    /* Empty state box */
    .metro-empty-state {{
        text-align: center;
        padding: 2.5rem 1.5rem;
        border: 1px dashed {THEME_COLORS["card_border"]};
        border-radius: 8px;
        background-color: rgba(30, 41, 59, 0.4);
        margin: 1rem 0;
    }}

    /* Button enhancements */
    div.stButton > button:first-child {{
        border-radius: 6px;
        font-weight: 600;
    }}
</style>
"""


def apply_theme_css() -> str:
    """Returns CSS string to inject into Streamlit via st.markdown."""
    return CUSTOM_CSS
