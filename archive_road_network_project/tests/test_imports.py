from importlib import import_module
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from config import PROJECT_ROOT
from scripts.verify_setup import PAGE_FILES, REQUIRED_DIRS, REQUIRED_FILES


@pytest.mark.parametrize(
    "module",
    (
        "config",
        "app",
        "src.graph",
        "src.algorithms",
        "src.analytics",
        "src.partitioning",
        "src.indexing",
        "src.simulation",
        "src.benchmarks",
        "src.visualization",
        "src.ui",
        "src.utils.paths",
        "src.utils.logger",
    ),
)
def test_core_imports(module: str) -> None:
    assert import_module(module).__name__ == module


def test_project_structure() -> None:
    for directory in REQUIRED_DIRS:
        assert (PROJECT_ROOT / directory).is_dir(), directory
    for filename in (*REQUIRED_FILES, *PAGE_FILES):
        assert (PROJECT_ROOT / filename).is_file(), filename


@pytest.mark.parametrize("filename", ("app.py", *PAGE_FILES))
def test_streamlit_sources(filename: str) -> None:
    path = PROJECT_ROOT / filename
    compile(path.read_bytes(), filename, "exec")
    if filename != "app.py":
        assert import_module(f"pages.{Path(filename).stem}")


def test_dashboard_home_and_navigation() -> None:
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert app.title[0].value == "SmartRoute Analytics"
    assert "Phase 3 of 12" in app.info[0].value
    titles = (
        "Route Optimizer",
        "Traffic Simulator",
        "Graph Analytics",
        "Partitioning",
        "Algorithm Lab",
        "Results & Export",
    )
    for page, title in zip(PAGE_FILES[1:], titles, strict=True):
        app.switch_page(page).run(timeout=30)
        assert not app.exception
        assert app.title[0].value == title
        if title == "Route Optimizer":
            app.button[0].click().run(timeout=30)
            assert not app.exception
            assert app.success[0].value == "Route validated"
        elif title == "Traffic Simulator":
            app.button[2].click().run(timeout=30)
            assert not app.exception
            assert app.success[0].value == "Simulation complete · ok"
        elif title == "Graph Analytics":
            for algorithm in ("BFS", "DFS"):
                app.radio[0].set_value(algorithm)
                app.text_input[1].set_value("1")
                app.button[0].click().run(timeout=30)
                assert not app.exception
                assert app.success[0].value == "Reachable · directed hops: 1"
                assert any("Strong components: 6" in item.value for item in app.markdown)
        elif title == "Partitioning":
            app.button[0].click().run(timeout=30)
            assert not app.exception
            assert "Partitioned into" in app.success[0].value
        elif title == "Algorithm Lab":
            app.button[0].click().run(timeout=30)
            assert not app.exception
            assert "saved to" in app.success[0].value
        elif title == "Results & Export":
            assert not app.exception
        else:
            assert app.info[0].value == "Planned for a later development phase"
