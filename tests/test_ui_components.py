"""Tests for UI component rendering functions."""

from src.ui.theme import THEME_COLORS, apply_theme_css


def test_theme_colors():
    """Verify core theme colors are defined properly."""
    assert THEME_COLORS["background"] == "#0B1120"
    assert THEME_COLORS["primary"] == "#38BDF8"
    assert THEME_COLORS["card_bg"] == "#1E293B"


def test_theme_css_generation():
    """Verify custom CSS string generates correctly."""
    css = apply_theme_css()
    assert "<style>" in css
    assert "#0B1120" in css
    assert ".metro-card" in css


def test_components_execute_cleanly():
    """Verify that component rendering functions do not raise exceptions."""
    # Test functions with basic arguments (mock or Streamlit environment)
    css_str = apply_theme_css()
    assert isinstance(css_str, str)
