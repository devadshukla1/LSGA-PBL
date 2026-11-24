"""Unit tests for clean imports across core packages and Streamlit pages."""

import py_compile

from config import PROJECT_ROOT


def test_core_package_imports():
    """Verify that all core project modules import without error."""
    import config
    import src.core.exceptions
    import src.core.logging_config
    import src.core.settings
    import src.data.loader
    import src.data.schemas
    import src.graph.metro_builder
    import src.graph.validator
    import src.ui.components
    import src.ui.sidebar
    import src.ui.theme
    import src.visualization.metro_plot

    assert config.APP_NAME == "MetroGraph Analytics"
    assert src.visualization.metro_plot.create_metro_network_plot is not None


def test_streamlit_pages_syntax():
    """Verify that all Streamlit page scripts compile without syntax errors."""
    pages_dir = PROJECT_ROOT / "pages"
    page_files = list(pages_dir.glob("*.py"))
    assert len(page_files) == 5, f"Expected 5 Streamlit pages, found {len(page_files)}: {page_files}"

    for page_path in page_files:
        # py_compile checks syntax without executing runtime Streamlit server loops
        py_compile.compile(str(page_path), doraise=True)

    # Check app.py as well
    py_compile.compile(str(PROJECT_ROOT / "app.py"), doraise=True)
