"""Resolve paths within the project and initialize its writable directories."""

from pathlib import Path, PureWindowsPath

from config import LOGS_DIR, PROJECT_ROOT, WORKSPACE_DIRECTORIES


def project_path(relative_path: str | Path) -> Path:
    """Resolve a relative path, rejecting traversal, drives, and escaping symlinks."""
    windows_path = PureWindowsPath(relative_path)
    if windows_path.anchor or ".." in windows_path.parts:
        raise ValueError(f"Expected a project-relative path: {relative_path}")

    root = PROJECT_ROOT.resolve()
    destination = root.joinpath(*windows_path.parts).resolve()
    if not destination.is_relative_to(root):
        raise ValueError(f"Path escapes the project root: {relative_path}")
    return destination


def initialize_directories() -> None:
    """Create data and results directories explicitly when a caller needs them."""
    for directory in WORKSPACE_DIRECTORIES:
        project_path(directory.relative_to(PROJECT_ROOT)).mkdir(parents=True, exist_ok=True)


def initialize_log_directory() -> Path:
    """Create and return the project log directory for file logging."""
    directory = project_path(LOGS_DIR.relative_to(PROJECT_ROOT))
    directory.mkdir(parents=True, exist_ok=True)
    return directory
