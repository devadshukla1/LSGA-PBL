"""Setup and environment verification script for MetroGraph Analytics Phase 1.

Verifies:
1. Python version (>=3.11, <3.13)
2. Dependency imports
3. Project paths
4. Dataset files
5. CSV schema
6. Graph construction
7. Graph validation
8. Plotly visualization creation
9. Streamlit page files
10. Logging initialization
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_checks() -> bool:
    checks = []

    # 1. Python version
    major, minor = sys.version_info.major, sys.version_info.minor
    py_ok = (major == 3 and minor in (11, 12))
    checks.append(("Python version >= 3.11 and < 3.13", py_ok, f"Current: {major}.{minor}"))

    # 2. Dependency imports
    try:
        import networkx
        import numpy
        import pandas
        import plotly
        import pytest
        import ruff
        import streamlit

        assert networkx.__name__ == "networkx"
        assert numpy.__name__ == "numpy"
        assert pandas.__name__ == "pandas"
        assert plotly.__name__ == "plotly"
        assert pytest.__name__ == "pytest"
        assert ruff.__name__ == "ruff"
        assert streamlit.__name__ == "streamlit"

        dep_ok = True
        dep_msg = "networkx, pandas, numpy, plotly, streamlit, pytest, ruff present"
    except ImportError as e:
        dep_ok = False
        dep_msg = str(e)
    checks.append(("Core dependency imports", dep_ok, dep_msg))

    # 3. Project paths
    try:
        from config import (
            CACHE_DIR,
            DATA_DIR,
            EXPORTS_DIR,
            LOGS_DIR,
            PROCESSED_DATA_DIR,
            SAMPLE_DATA_DIR,
        )

        paths_ok = all(
            p.exists()
            for p in [DATA_DIR, SAMPLE_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR, EXPORTS_DIR, LOGS_DIR]
        )
        paths_msg = "All core directories exist"
    except Exception as e:
        paths_ok = False
        paths_msg = str(e)
    checks.append(("Project paths resolution", paths_ok, paths_msg))

    # 4. Dataset files
    try:
        from config import SAMPLE_DATA_DIR

        stn_file = (SAMPLE_DATA_DIR / "stations.csv").is_file()
        lin_file = (SAMPLE_DATA_DIR / "lines.csv").is_file()
        con_file = (SAMPLE_DATA_DIR / "connections.csv").is_file()
        data_files_ok = stn_file and lin_file and con_file
        data_files_msg = "stations.csv, lines.csv, connections.csv exist"
    except Exception as e:
        data_files_ok = False
        data_files_msg = str(e)
    checks.append(("Dataset files existence", data_files_ok, data_files_msg))

    # 5. CSV schema & loading
    try:
        from src.data.loader import load_validated_dataset

        stations_df, lines_df, connections_df, station_lines_df, metadata = load_validated_dataset()
        csv_ok = len(stations_df) >= 10 and len(lines_df) >= 3 and len(connections_df) >= 10
        csv_msg = f"{len(stations_df)} stations, {len(lines_df)} lines, {len(connections_df)} connections"
    except Exception as e:
        csv_ok = False
        csv_msg = str(e)
    checks.append(("CSV schema validation", csv_ok, csv_msg))

    # 6. Graph construction
    try:
        import networkx as nx

        from src.graph.metro_builder import build_metro_graph

        graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)
        builder_ok = isinstance(graph, nx.MultiGraph) and graph.number_of_nodes() > 0
        builder_msg = f"MultiGraph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges"
    except Exception as e:
        builder_ok = False
        builder_msg = str(e)
    checks.append(("Graph construction", builder_ok, builder_msg))

    # 7. Graph validation
    try:
        from src.graph.validator import validate_metro_graph

        val_summary = validate_metro_graph(graph)
        val_ok = val_summary["is_valid"] and val_summary["is_connected"]
        val_msg = (
            f"Connected: {val_summary['is_connected']}, "
            f"Interchange Hubs: {val_summary['interchange_station_count']}"
        )
    except Exception as e:
        val_ok = False
        val_msg = str(e)
    checks.append(("Graph structural validation", val_ok, val_msg))

    # 8. Plotly visualization creation
    try:
        import plotly.graph_objects as go

        from src.visualization.metro_plot import create_metro_network_plot

        fig = create_metro_network_plot(graph)
        plot_ok = isinstance(fig, go.Figure) and len(fig.data) > 0
        plot_msg = f"Plotly Figure generated with {len(fig.data)} traces"
    except Exception as e:
        plot_ok = False
        plot_msg = str(e)
    checks.append(("Offline Plotly visualization", plot_ok, plot_msg))

    # 9. Streamlit page files
    try:
        pages_dir = PROJECT_ROOT / "pages"
        pages = list(pages_dir.glob("*.py"))
        pages_ok = len(pages) == 6 and (PROJECT_ROOT / "app.py").is_file()
        pages_msg = f"{len(pages)} subpages found + app.py"
    except Exception as e:
        pages_ok = False
        pages_msg = str(e)
    checks.append(("Streamlit page structure", pages_ok, pages_msg))

    # 10. Logging initialization
    try:
        from src.core.logging_config import configure_logging, get_logger

        configure_logging()
        logger = get_logger("metrograph.verify")
        logger.info("Verification script test log entry.")
        log_ok = (PROJECT_ROOT / "logs" / "metrograph.log").is_file()
        log_msg = "Logging initialized and verified in logs/metrograph.log"
    except Exception as e:
        log_ok = False
        log_msg = str(e)
    checks.append(("Logging initialization", log_ok, log_msg))

    # Print Report
    print("=" * 70)
    print(" METROGRAPH ANALYTICS - SETUP VERIFICATION REPORT")
    print("=" * 70)
    all_passed = True
    for name, status, details in checks:
        tag = "[ PASS ]" if status else "[ FAIL ]"
        if not status:
            all_passed = False
        print(f"{tag} {name.ljust(35)} : {details}")
    print("=" * 70)

    if all_passed:
        print("OVERALL RESULT: PASS")
    else:
        print("OVERALL RESULT: FAIL")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
