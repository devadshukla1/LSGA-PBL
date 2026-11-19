from pathlib import Path

import pytest

from src.utils import paths


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(paths, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(paths, "WORKSPACE_DIRECTORIES", (tmp_path / "data" / "raw",))
    monkeypatch.setattr(paths, "LOGS_DIR", tmp_path / "logs")
    return tmp_path
