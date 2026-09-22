import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from helpers import MergeHarness


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        '--exe',
        required=True,
        help="Path to the merge executable",
    )
    parser.addoption(
        '--valgrind-wrapper',
        default=None,
        help="Path to the valgrind wrapper script (e.g. ci-extra/run-valgrind.sh)",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line('markers', 'slow: marks tests as slow (skipped under valgrind)')


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption('--valgrind-wrapper') is None:
        return

    skip_slow = pytest.mark.skip(reason="Skipped under valgrind")
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def mh(pytestconfig: pytest.Config, tmp_path: Path) -> MergeHarness:
    executable = Path(pytestconfig.getoption('--exe'))
    assert executable.is_file(), f"Executable not found: {executable}"

    cmd_prefix = [executable]
    wrapper = pytestconfig.getoption('--valgrind-wrapper')
    if wrapper is not None:
        cmd_prefix.insert(0, wrapper)

    def run_merge(
        file_paths: Sequence[str | Path],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[bytes]:
        cmd = cmd_prefix.copy()
        cmd.extend(p for p in file_paths)
        kwargs.setdefault('stdout', subprocess.PIPE)
        kwargs.setdefault('stderr', subprocess.PIPE)
        kwargs.setdefault('timeout', 20)
        return subprocess.run(cmd, **kwargs)

    return MergeHarness(run_merge, tmp_path, under_valgrind=wrapper is not None)
