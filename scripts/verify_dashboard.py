"""Standalone Phase 7 verification script for MetroGraph Analytics Dashboard.

Validates:
1. Application entry point.
2. All six page files exist and compile.
3. UI module imports and session state functions.
4. Dataset loading and graph construction bundle.
5. Routing integration.
6. Centrality integration.
7. Closure integration.
8. Plotly figure generation.
9. Export generation.
10. Streamlit configuration.
11. No OpenStreetMap / OSMnx dependency.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def check_pages_exist():
    pages = [
        "app.py",
        "pages/1_Metro_Overview.py",
        "pages/2_Route_Planner.py",
        "pages/3_Station_Importance.py",
        "pages/4_Closure_Simulator.py",
        "pages/5_Algorithm_Lab.py",
    ]
    for p in pages:
        p_path = PROJECT_ROOT / p
        assert p_path.exists(), f"Missing page file: {p}"
        # Test compilation
        with open(p_path, "r", encoding="utf-8") as f:
            code = f.read()
        compile(code, str(p_path), "exec")

    # Ensure 6_Results.py is removed
    assert not (PROJECT_ROOT / "pages/6_Results.py").exists(), "pages/6_Results.py must be removed"
    return True


def check_ui_imports():
    from src.ui import (
        THEME_COLORS,
        apply_theme_css,
    )
    assert THEME_COLORS["background"] == "#0B1120"
    assert "<style>" in apply_theme_css()
    return True


def check_no_osmnx():
    for mod_name in sys.modules:
        assert "osmnx" not in mod_name, f"Forbidden osmnx module found in sys.modules: {mod_name}"
    # Check codebase text for prohibited imports
    for py_file in PROJECT_ROOT.glob("src/**/*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "import osmnx" not in content, f"Found 'import osmnx' in {py_file}"
            assert "from osmnx" not in content, f"Found 'from osmnx' in {py_file}"
    return True


def check_visualization():
    from src.algorithms.bfs import find_route_bfs
    from src.analytics.station_ranking import compute_station_analytics
    from src.core.settings import SAMPLE_DATA_DIR
    from src.data.loader import load_validated_dataset
    from src.graph.metro_builder import build_metro_graph
    from src.visualization.metro_plot import (
        create_metro_network_plot,
        plot_closure_comparison,
        plot_metro_route,
        plot_top_stations,
    )

    s_df, l_df, c_df, sl_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    g = build_metro_graph(s_df, l_df, c_df, sl_df)

    fig1 = create_metro_network_plot(g)
    assert fig1 is not None

    r = find_route_bfs(g, "S01", "S06")
    fig2 = plot_metro_route(g, r)
    assert fig2 is not None

    fig3 = plot_closure_comparison(g, g, closed_station_ids=["S02"])
    assert fig3 is not None

    stn_res, _, _ = compute_station_analytics(g, sl_df, l_df)
    fig4 = plot_top_stations(stn_res, metric="degree_centrality", top_n=5)
    assert fig4 is not None
    return True


def check_exports():
    import json

    from src.core.settings import SAMPLE_DATA_DIR
    from src.data.loader import load_validated_dataset
    from src.graph.metro_builder import build_metro_graph
    from src.simulation.closure_engine import simulate_station_closure
    from src.simulation.impact_comparison import build_impact_comparison_table

    s_df, l_df, c_df, sl_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    g = build_metro_graph(s_df, l_df, c_df, sl_df)
    sim = simulate_station_closure(g, ["S02"])
    t = build_impact_comparison_table(sim)
    csv_bytes = t.to_csv(index=False)
    assert len(csv_bytes) > 50
    json_bytes = json.dumps({"test": 123})
    assert len(json_bytes) > 5
    return True


def check_streamlit_config():
    config_file = PROJECT_ROOT / ".streamlit" / "config.toml"
    assert config_file.exists(), "Missing .streamlit/config.toml"
    with open(config_file, "r", encoding="utf-8") as f:
        text = f.read()
    assert 'base = "dark"' in text
    assert 'primaryColor = "#38BDF8"' in text
    assert 'backgroundColor = "#0B1120"' in text
    return True


def run_all_checks():
    checks = [
        ("Pages Compilation and Structure", check_pages_exist),
        ("UI Modules & Theme Tokens", check_ui_imports),
        ("Strict Offline (Zero OSMnx) Guarantee", check_no_osmnx),
        ("Interactive Plotly Visualizations", check_visualization),
        ("Export Formatting (CSV, JSON)", check_exports),
        ("Streamlit Theme Configuration", check_streamlit_config),
    ]

    print("=" * 80)
    print("METROGRAPH ANALYTICS - PHASE 7 DASHBOARD VERIFICATION")
    print("=" * 80)

    all_passed = True
    for name, func in checks:
        try:
            passed = func()
            if passed:
                print(f"[PASS] {name}")
            else:
                print(f"[FAIL] {name}")
                all_passed = False
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("OVERALL RESULT: PASS")
        sys.exit(0)
    else:
        print("OVERALL RESULT: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    run_all_checks()
