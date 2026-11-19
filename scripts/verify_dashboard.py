"""Automated verification script for Phase 10: Streamlit Dashboard & Integration."""

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import PROJECT_ROOT
from src.ui.formatting import (
    format_distance,
    format_memory,
    format_percentage,
    format_runtime,
    format_time,
)
from src.ui.theme import COLOR_PALETTE


def verify_dashboard() -> bool:
    print("=" * 65)
    print("SMART CITY TRAFFIC & EMERGENCY ROUTE OPTIMIZER")
    print("PHASE 10: Streamlit Dashboard & System Integration Verification")
    print("=" * 65)

    checklist = []

    # 1. UI Formatting & Theme
    try:
        assert COLOR_PALETTE["primary_sky"] == "#38BDF8"
        assert format_distance(1500) == "1.50 km"
        assert format_time(90) == "1 min 30 s"
        assert format_runtime(0.002) == "2.00 ms"
        assert format_memory(2.5) == "2.50 MB"
        assert format_percentage(0.5) == "50.0%"
        checklist.append(("UI Formatting & Theme tokens", True, "All formatters valid"))
    except Exception as err:
        checklist.append(("UI Formatting & Theme tokens", False, str(err)))

    # 2. App Boot & Overview Page
    try:
        app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
        assert not app.exception
        assert app.title[0].value == "SmartRoute Analytics"
        checklist.append(("App Boot & Overview navigation", True, "Title rendered cleanly"))
    except Exception as err:
        checklist.append(("App Boot & Overview navigation", False, str(err)))
        return False

    # 3. Route Optimizer Page Execution
    try:
        app.switch_page("pages/2_Route_Optimizer.py").run(timeout=30)
        assert not app.exception
        assert app.title[0].value == "Route Optimizer"
        app.button[0].click().run(timeout=30)
        assert not app.exception
        assert app.success[0].value == "Route validated"
        checklist.append(("Route Optimizer live execution", True, "Route validated & rendered"))
    except Exception as err:
        checklist.append(("Route Optimizer live execution", False, str(err)))

    # 4. Traffic Simulator Page Execution
    try:
        app.switch_page("pages/3_Traffic_Simulator.py").run(timeout=30)
        assert not app.exception
        assert app.title[0].value == "Traffic Simulator"
        app.button[2].click().run(timeout=30)
        assert not app.exception
        assert app.success[0].value == "Simulation complete · ok"
        checklist.append(("Traffic Simulator live execution", True, "Simulation scenario complete"))
    except Exception as err:
        checklist.append(("Traffic Simulator live execution", False, str(err)))

    # 5. Graph Analytics Page Execution
    try:
        app.switch_page("pages/4_Graph_Analytics.py").run(timeout=30)
        assert not app.exception
        assert app.title[0].value == "Graph Analytics"
        app.radio[0].set_value("BFS")
        app.text_input[1].set_value("1")
        app.button[0].click().run(timeout=30)
        assert not app.exception
        assert "Reachable" in app.success[0].value
        checklist.append(("Graph Analytics traversal & components", True, "BFS hops evaluated"))
    except Exception as err:
        checklist.append(("Graph Analytics traversal & components", False, str(err)))

    # 6. Partitioning Page Execution
    try:
        app.switch_page("pages/5_Partitioning.py").run(timeout=30)
        assert not app.exception
        assert app.title[0].value == "Partitioning"
        app.button[0].click().run(timeout=30)
        assert not app.exception
        assert "Partitioned into" in app.success[0].value
        checklist.append(("Partitioning live execution", True, "Graph partitioned into regions"))
    except Exception as err:
        checklist.append(("Partitioning live execution", False, str(err)))

    # 7. Algorithm Lab Page Execution
    try:
        app.switch_page("pages/6_Algorithm_Lab.py").run(timeout=30)
        assert not app.exception
        assert app.title[0].value == "Algorithm Lab"
        app.button[0].click().run(timeout=30)
        assert not app.exception
        assert "saved to" in app.success[0].value
        checklist.append(("Algorithm Lab empirical run", True, "Benchmark execution & export ok"))
    except Exception as err:
        checklist.append(("Algorithm Lab empirical run", False, str(err)))

    # 8. Results & Export Page Execution
    try:
        app.switch_page("pages/7_Results.py").run(timeout=30)
        assert not app.exception
        assert app.title[0].value == "Results & Export"
        checklist.append(("Results & Export dashboard", True, "Historical runs loaded"))
    except Exception as err:
        checklist.append(("Results & Export dashboard", False, str(err)))

    print("\n" + "=" * 65)
    print("CHECKLIST RESULTS:")
    print("=" * 65)
    all_pass = True
    for item, passed, detail in checklist:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {item}: {detail}")
        if not passed:
            all_pass = False

    print("=" * 65)
    if all_pass:
        print("PHASE 10 VERIFICATION: PASS")
    else:
        print("PHASE 10 VERIFICATION: FAIL")
    print("=" * 65)
    return all_pass


if __name__ == "__main__":
    success = verify_dashboard()
    sys.exit(0 if success else 1)
