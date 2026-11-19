from collections.abc import Iterator
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

from src.utils.logger import configure_logging, get_logger


@pytest.fixture(autouse=True)
def restore_logger() -> Iterator[None]:
    logger = get_logger()
    previous_level, previous_propagate = logger.level, logger.propagate
    yield
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(previous_level)
    logger.propagate = previous_propagate


def test_console_level_and_handler_count(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("WARNING")
    configure_logging("WARNING")
    logger = get_logger("tests")
    assert logger.name == "smartroute.tests"
    assert len(get_logger().handlers) == 1
    logger.info("hidden message")
    logger.warning("shown message")
    stderr = capsys.readouterr().err
    assert "hidden message" not in stderr
    assert stderr.count("WARNING smartroute.tests shown message") == 1


def test_file_logging_is_opt_in(workspace: Path) -> None:
    configure_logging()
    assert not (workspace / "logs").exists()
    configure_logging("DEBUG", file_logging=True)
    configure_logging("DEBUG", file_logging=True)
    assert len(get_logger().handlers) == 2
    assert any(isinstance(handler, RotatingFileHandler) for handler in get_logger().handlers)
    get_logger("tests").debug("persisted message")
    log = workspace / "logs" / "smartroute.log"
    assert log.read_text(encoding="utf-8").count("DEBUG smartroute.tests persisted message") == 1


def test_file_logging_fallback(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    blocked = tmp_path / "file"
    blocked.touch()
    configure_logging(file_logging=True, log_dir=blocked)
    assert len(get_logger().handlers) == 1
    assert "Continuing with console logging" in capsys.readouterr().err
