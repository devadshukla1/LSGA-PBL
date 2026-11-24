import subprocess
import sys
from pathlib import Path

import pytest

from src.utils.paths import initialize_directories, project_path


def test_resolve_and_create(workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(workspace.parent)
    expected = workspace / "data" / "raw"
    assert project_path("data/raw") == expected
    assert project_path(r"data\raw") == expected
    assert not expected.exists()
    initialize_directories()
    initialize_directories()
    assert expected.is_dir()
    assert not (workspace / "logs").exists()


@pytest.mark.parametrize("invalid", ["../escape", r"data\..\escape", "/tmp", r"C:\temp", "C:temp"])
def test_rejects_unsafe_paths(workspace: Path, invalid: str) -> None:
    with pytest.raises(ValueError, match="project-relative"):
        project_path(invalid)


def test_rejects_escaping_directory_link(workspace: Path) -> None:
    link = workspace / "linked"
    target = workspace.parent / f"{workspace.name}-outside"
    target.mkdir()
    if sys.platform == "win32":
        subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            check=True,
            capture_output=True,
        )
    else:
        link.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes"):
        project_path("linked/outside")
