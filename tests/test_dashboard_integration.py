"""Integration tests for Streamlit pages and dashboard session state."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_app_landing_page():
    """Verify app.py entry point runs cleanly in headless AppTest."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"app.py raised exception: {at.exception}"


def test_page_metro_overview():
    """Verify 1_Metro_Overview.py page runs without errors."""
    at = AppTest.from_file(str(PROJECT_ROOT / "pages" / "1_Metro_Overview.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"1_Metro_Overview.py raised exception: {at.exception}"


def test_page_route_planner():
    """Verify 2_Route_Planner.py page runs without errors."""
    at = AppTest.from_file(str(PROJECT_ROOT / "pages" / "2_Route_Planner.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"2_Route_Planner.py raised exception: {at.exception}"


def test_page_station_importance():
    """Verify 3_Station_Importance.py page runs without errors."""
    at = AppTest.from_file(str(PROJECT_ROOT / "pages" / "3_Station_Importance.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"3_Station_Importance.py raised exception: {at.exception}"


def test_page_closure_simulator():
    """Verify 4_Closure_Simulator.py page runs without errors."""
    at = AppTest.from_file(str(PROJECT_ROOT / "pages" / "4_Closure_Simulator.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"4_Closure_Simulator.py raised exception: {at.exception}"


def test_page_algorithm_lab():
    """Verify 5_Algorithm_Lab.py page runs without errors."""
    at = AppTest.from_file(str(PROJECT_ROOT / "pages" / "5_Algorithm_Lab.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"5_Algorithm_Lab.py raised exception: {at.exception}"


def test_results_page_absent():
    """Verify 6_Results.py is completely absent from pages directory."""
    results_path = PROJECT_ROOT / "pages" / "6_Results.py"
    assert not results_path.exists(), "6_Results.py should be removed from pages/"

