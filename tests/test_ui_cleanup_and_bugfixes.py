"""Tests verifying FIX 1 through FIX 5:
- Algorithm Lab runtime charts and column references
- Complete absence of Results page and navigation
- Complete absence of Synthetic Sample in production UI
- Complete absence of Runtime Parameters, Development Phases, and Phase 7 Build footer
- Pure 5-page sidebar navigation and Delhi Metro active dataset
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.algorithms.comparison import compare_routing_algorithms
from src.core.settings import METRO_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.ui.sidebar import get_active_dataset_directory

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_algorithm_lab_runtime_column_compatibility():
    """Verify comparison dataframe produced by routing algorithms has 'Runtime (ms)' column."""
    stns, lines, conns, sl, meta = load_validated_dataset(METRO_DATA_DIR)
    graph = build_metro_graph(stns, lines, conns, sl)
    comp_df, _ = compare_routing_algorithms(graph, "STN001", "STN005")

    assert "Runtime (ms)" in comp_df.columns
    assert "Algorithm" in comp_df.columns
    assert "Modeled Journey Time (min)" in comp_df.columns
    assert "Transfers" in comp_df.columns


def test_results_page_file_and_routes_removed():
    """Verify 6_Results.py is deleted and no routes or references point to it."""
    results_file = PROJECT_ROOT / "pages" / "6_Results.py"
    assert not results_file.exists(), "pages/6_Results.py must not exist"

    # Verify only the 5 permitted pages exist in pages/
    existing_pages = sorted([p.name for p in (PROJECT_ROOT / "pages").glob("*.py")])
    assert existing_pages == [
        "1_Metro_Overview.py",
        "2_Route_Planner.py",
        "3_Station_Importance.py",
        "4_Closure_Simulator.py",
        "5_Algorithm_Lab.py",
    ]


def test_sidebar_contains_only_delhi_metro_and_no_unwanted_sections():
    """Verify sidebar rendering contains NO Synthetic Sample, Runtime Parameters, or Phase badges."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception

    # Extract all text from markdown and caption elements in sidebar
    sidebar_texts = []
    for md in at.sidebar.markdown:
        sidebar_texts.append(md.value)
    for cap in at.sidebar.caption:
        sidebar_texts.append(cap.value)
    for suc in at.sidebar.success:
        sidebar_texts.append(suc.value)

    rendered_text = " ".join(sidebar_texts)

    # Unwanted strings must NOT be in sidebar
    assert "Synthetic Sample" not in rendered_text
    assert "Synthetic Sample (12 stns)" not in rendered_text
    assert "Runtime Parameters" not in rendered_text
    assert "Development Phases" not in rendered_text
    assert "Phase 7 Build" not in rendered_text
    assert "Results" not in rendered_text

    # Required strings MUST be present
    assert "Delhi Metro Network (Real NCR)" in rendered_text
    assert "Delhi Metro: Loaded & Verified" in rendered_text


def test_production_active_dataset_is_strictly_delhi_metro():
    """Verify default session state and active dataset directory enforce Delhi Metro."""
    active_dir = get_active_dataset_directory("delhi_metro")
    assert active_dir == METRO_DATA_DIR
    assert active_dir.exists()



def test_algorithm_lab_headless_run():
    """Verify 5_Algorithm_Lab.py page runs headlessly without ValueError or traceback."""
    at = AppTest.from_file(str(PROJECT_ROOT / "pages" / "5_Algorithm_Lab.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"5_Algorithm_Lab.py crashed: {at.exception}"
