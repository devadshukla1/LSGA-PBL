"""UI theme, components, state management, and formatting for SmartRoute Analytics."""

from src.ui.components import (
    render_badge,
    render_empty_state,
    render_metric_card,
    render_page_header,
    render_section_header,
)
from src.ui.errors import display_error, handle_ui_exception
from src.ui.formatting import (
    format_distance,
    format_memory,
    format_percentage,
    format_runtime,
    format_time,
)
from src.ui.sidebar import render_app_sidebar
from src.ui.state import (
    ensure_session_state,
    get_active_dataset_id,
    invalidate_dataset_state,
    set_active_dataset_id,
)
from src.ui.theme import COLOR_PALETTE, inject_custom_theme

__all__ = [
    "COLOR_PALETTE",
    "display_error",
    "ensure_session_state",
    "format_distance",
    "format_memory",
    "format_percentage",
    "format_runtime",
    "format_time",
    "get_active_dataset_id",
    "handle_ui_exception",
    "inject_custom_theme",
    "invalidate_dataset_state",
    "render_app_sidebar",
    "render_badge",
    "render_empty_state",
    "render_metric_card",
    "render_page_header",
    "render_section_header",
    "set_active_dataset_id",
]
