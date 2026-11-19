"""Smoke tests for all seven Streamlit dashboard pages."""

from streamlit.testing.v1 import AppTest

from config import PROJECT_ROOT


def test_overview_smoke() -> None:
    """Verify Overview page renders metrics, datasets, and tabs without errors."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert app.title[0].value == "SmartRoute Analytics"
    assert len(app.metric) >= 4


def test_route_optimizer_smoke() -> None:
    """Verify Route Optimizer page executes and displays route output."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    app.switch_page("pages/2_Route_Optimizer.py").run(timeout=30)
    assert not app.exception
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert app.success[0].value == "Route validated"


def test_traffic_simulator_smoke() -> None:
    """Verify Traffic Simulator page executes simulation run cleanly."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    app.switch_page("pages/3_Traffic_Simulator.py").run(timeout=30)
    assert not app.exception
    app.button[2].click().run(timeout=30)
    assert not app.exception
    assert "Simulation complete" in app.success[0].value


def test_graph_analytics_smoke() -> None:
    """Verify Graph Analytics page runs traversal."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    app.switch_page("pages/4_Graph_Analytics.py").run(timeout=30)
    assert not app.exception
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert not app.exception


def test_partitioning_smoke() -> None:
    """Verify Partitioning page computes partitions."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    app.switch_page("pages/5_Partitioning.py").run(timeout=30)
    assert not app.exception
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert "Partitioned into" in app.success[0].value


def test_algorithm_lab_smoke() -> None:
    """Verify Algorithm Lab page executes and reports saved experiment."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    app.switch_page("pages/6_Algorithm_Lab.py").run(timeout=30)
    assert not app.exception
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert "saved to" in app.success[0].value


def test_results_page_smoke() -> None:
    """Verify Results page loads saved manifests and summaries."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    app.switch_page("pages/7_Results.py").run(timeout=30)
    assert not app.exception
    assert app.title[0].value == "Results & Export"
