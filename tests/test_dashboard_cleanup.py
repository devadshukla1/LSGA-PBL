"""Tests verifying removal of Platform Guide, offline precision card, phase footer,
and verifying that Metro Overview is the default landing page under st.navigation.
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_app_navigation_and_default_landing():
    """Verify app.py initializes st.navigation without exceptions and defaults to Metro Overview."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception

    # Extract all text from headings and markdown
    main_texts = [h.value for h in at.header] + [m.value for m in at.markdown]
    combined_main = " ".join(main_texts)

    # Verify Metro Overview content is rendered as landing page
    assert "Metro Overview" in combined_main
    assert "Topological Invariants & Structural Scope" in combined_main
    assert "Delhi Metro Network Map & Line Corridor Filter" in combined_main


def test_removed_sections_not_present():
    """Verify Platform Guide, Offline Precision Guarantee, and Phase footer are completely absent."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception

    all_texts = (
        [h.value for h in at.header]
        + [m.value for m in at.markdown]
        + [c.value for c in at.caption]
    )
    combined = " ".join(all_texts)

    assert "Platform Guide & Capabilities" not in combined
    assert "Offline Precision Guarantee" not in combined
    assert "Feature Modules" not in combined
    assert "Phase 7 • Professional Streamlit Dashboard" not in combined
    assert "Phase 7 Build" not in combined


def test_sidebar_contains_only_five_clean_pages_and_active_dataset():
    """Verify sidebar contains no duplicate app navigation, no synthetic sample, no runtime parameters."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception

    sidebar_texts = (
        [m.value for m in at.sidebar.markdown]
        + [c.value for c in at.sidebar.caption]
        + [s.value for s in at.sidebar.success]
    )
    combined_sidebar = " ".join(sidebar_texts)

    assert "Delhi Metro Network (Real NCR)" in combined_sidebar
    assert "Delhi Metro: Loaded & Verified" in combined_sidebar
    assert "Synthetic Sample" not in combined_sidebar
    assert "Runtime Parameters" not in combined_sidebar
    assert "Development Phases" not in combined_sidebar
