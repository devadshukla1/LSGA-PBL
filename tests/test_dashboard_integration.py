"""End-to-end integration tests for Streamlit application dashboard pages."""

from streamlit.testing.v1 import AppTest

from config import PROJECT_ROOT


def test_app_loads_successfully() -> None:
    """Verify application boots without unhandled exceptions."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert len(app.title) > 0
    assert app.title[0].value == "SmartRoute Analytics"


def test_route_optimizer_flow() -> None:
    """Verify Route Optimizer executes routing request and displays route metrics."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    app.switch_page("pages/2_Route_Optimizer.py").run(timeout=30)
    assert not app.exception
    assert app.title[0].value == "Route Optimizer"

    # Execute route form
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert app.success[0].value == "Route validated"
    # Verify metric cards are present
    assert len(app.metric) >= 4


def test_partitioning_page_flow() -> None:
    """Verify Partitioning page renders metrics and spatial indexing elements."""
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    app.switch_page("pages/5_Partitioning.py").run(timeout=30)
    assert not app.exception
    assert app.title[0].value == "Partitioning"

    # Click Run Partitioning
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert "Partitioned into" in app.success[0].value
