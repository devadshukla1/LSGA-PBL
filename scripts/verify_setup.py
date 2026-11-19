"""Verify a local development setup without starting Streamlit."""

import sys
import tomllib
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryFile

ROOT = Path(__file__).resolve().parents[1]
PAGE_FILES = (
    "pages/1_Overview.py",
    "pages/2_Route_Optimizer.py",
    "pages/3_Traffic_Simulator.py",
    "pages/4_Graph_Analytics.py",
    "pages/5_Partitioning.py",
    "pages/6_Algorithm_Lab.py",
    "pages/7_Results.py",
)
REQUIRED_DIRS = (
    "data/raw",
    "data/processed",
    "data/scenarios",
    "data/samples",
    "results/benchmarks",
    "results/figures",
    "results/exports",
    "logs",
    "docs",
    "src",
    "pages",
    "scripts",
    "tests",
)
REQUIRED_FILES = (
    "app.py",
    "config.py",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    ".python-version",
    ".gitignore",
    ".streamlit/config.toml",
    "README.md",
    "docs/development_setup.md",
    "scripts/verify_setup.py",
)
DEPENDENCIES = (
    "streamlit",
    "networkx",
    "osmnx",
    "numpy",
    "pandas",
    "plotly",
    "folium",
    "streamlit_folium",
    "scipy",
    "pytest",
    "ruff",
)


def main() -> int:
    """Print individual results and return a failing exit status if needed."""
    failed = False

    def report(label: str, passed: bool, detail: str = "") -> None:
        nonlocal failed
        failed |= not passed
        print(f"{'PASS' if passed else 'FAIL'} {label}" + (f" ({detail})" if detail else ""))

    report("Python 3.11", sys.version_info[:2] == (3, 11), sys.version.split()[0])
    sys.path.insert(0, str(ROOT))
    for name in (*DEPENDENCIES, "config"):
        try:
            module = import_module(name)
            if name == "config" and module.CONFIG.project_root != ROOT:
                raise ValueError("wrong project root")
        except Exception as error:
            report(f"Import {name}", False, str(error))
        else:
            report(f"Import {name}", True)

    missing = [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]
    missing += [name for name in REQUIRED_DIRS if not (ROOT / name).is_dir()]
    report("Project structure", not missing, ", ".join(missing))

    for name in REQUIRED_DIRS[:8]:
        try:
            with TemporaryFile(dir=ROOT / name) as probe:
                probe.write(b"ok")
        except OSError as error:
            report(f"Writable {name}", False, str(error))
        else:
            report(f"Writable {name}", True)

    for name in ("app.py", *PAGE_FILES):
        try:
            compile((ROOT / name).read_bytes(), name, "exec")
        except (OSError, SyntaxError) as error:
            report(name, False, str(error))
        else:
            report(name, True)

    try:
        settings = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        report(
            "pytest discovery", "tests" in settings["tool"]["pytest"]["ini_options"]["testpaths"]
        )
    except (OSError, KeyError, ValueError, TypeError) as error:
        report("pytest discovery", False, str(error))

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
