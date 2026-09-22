from pathlib import Path

import pytest

import tests.repl_test as repl_test
from tests.error_registry import error_registry


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption('--exe', type=Path, required=True, help="Path to the app executable")


def pytest_configure(config: pytest.Config) -> None:
    repl_test.app_exe_path = config.getoption('--exe')


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    error_registry.dump()
