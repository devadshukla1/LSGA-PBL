"""Tests for UI formatting, components, error display, and theme utilities."""

import pytest
import streamlit as st

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
from src.ui.theme import COLOR_PALETTE, inject_custom_theme


def test_theme_color_tokens() -> None:
    """Verify core theme color palette tokens exist and follow hex formatting."""
    expected_keys = [
        "bg_dark",
        "card_bg",
        "card_border",
        "primary_sky",
        "accent_blue",
        "text_primary",
        "text_secondary",
        "success_green",
        "warning_amber",
        "error_red",
    ]
    for key in expected_keys:
        assert key in COLOR_PALETTE
        assert COLOR_PALETTE[key].startswith("#")


def test_format_distance() -> None:
    """Verify distance formatting across meters and kilometers boundaries."""
    assert format_distance(-10) == "0 m"
    assert format_distance(0) == "0.0 m"
    assert format_distance(450.5) == "450.5 m"
    assert format_distance(999.9) == "999.9 m"
    assert format_distance(1000) == "1.00 km"
    assert format_distance(2540.2) == "2.54 km"


def test_format_time() -> None:
    """Verify travel time formatting across seconds, minutes, and hours."""
    assert format_time(-5) == "0 s"
    assert format_time(0) == "0.0 s"
    assert format_time(42.3) == "42.3 s"
    assert format_time(60) == "1 min"
    assert format_time(125) == "2 min 5 s"
    assert format_time(3600) == "1 h 0 min"
    assert format_time(7320) == "2 h 2 min"


def test_format_runtime() -> None:
    """Verify execution runtime formatting across microsecond, millisecond, and second ranges."""
    assert format_runtime(-1) == "0.00 ms"
    assert format_runtime(0.000045) == "45.0 µs"
    assert format_runtime(0.0034) == "3.40 ms"
    assert format_runtime(0.245) == "245.00 ms"
    assert format_runtime(1.425) == "1.4250 s"


def test_format_memory() -> None:
    """Verify memory usage formatting across kilobytes and megabytes."""
    assert format_memory(-1) == "0.00 MB"
    assert format_memory(0.05) == "51.2 KB"
    assert format_memory(1.25) == "1.25 MB"
    assert format_memory(128.456) == "128.46 MB"


def test_format_percentage() -> None:
    """Verify percentage formatting."""
    assert format_percentage(0.0) == "0.0%"
    assert format_percentage(0.4285, decimals=1) == "42.9%"
    assert format_percentage(0.4285, decimals=2) == "42.85%"
    assert format_percentage(1.0) == "100.0%"


def test_render_components_without_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify rendering helpers execute cleanly in Streamlit session."""
    monkeypatch.setattr(st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(st, "title", lambda *args, **kwargs: None)
    monkeypatch.setattr(st, "subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr(st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(st, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(st, "error", lambda *args, **kwargs: None)
    monkeypatch.setattr(st, "metric", lambda *args, **kwargs: None)

    inject_custom_theme()
    render_page_header("Test Title", "Subtitle", "Phase 10")
    render_section_header("Section", "Caption")
    render_metric_card("Metric", "100", "+5")
    render_badge("Active", "success")
    render_badge("Pending", "warning")
    render_badge("Info", "info")
    render_empty_state("No data", "Please run analysis")
    display_error("Something went wrong", "Check input")
    handle_ui_exception(ValueError("Invalid argument"), context="Test context")
    render_app_sidebar()
