import itertools
import os
import random
import string
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

RunMerge = Callable[..., subprocess.CompletedProcess[bytes]]

ALL_BYTES_EXCEPT_NEWLINE = bytes(
    b for b in range(256)
    if b != ord('\n') and b != ord('\r')
)


def rand_bytes(max_length: int, rng: random.Random) -> bytes:
    length = rng.randint(0, max_length)
    return bytes(rng.choices(ALL_BYTES_EXCEPT_NEWLINE, k=length))


def all_strings_of_length(n: int, alphabet: str = string.ascii_lowercase) -> list[str]:
    return [''.join(chars) for chars in itertools.product(alphabet, repeat=n)]


def _gen_file(path: Path, lines: Sequence[bytes | str], sep: bytes | str) -> None:
    with open(path, 'wb') as f:
        for line in lines:
            f.write(_to_bytes(line))
            f.write(_to_bytes(sep))


def _to_bytes(line: bytes | str) -> bytes:
    if isinstance(line, bytes):
        return line
    else:
        return line.encode()


def _repr_line(line: bytes) -> str:
    return repr(line.decode(errors='replace'))


def _format_lines_inner(data: list[bytes] | bytes | None, tab: int = 2) -> str:
    if data is None:
        return f"{' ' * tab}<not captured>\n"
    if isinstance(data, bytes):
        lines = data.split(os.linesep.encode())
        if len(lines[-1]) == 0:
            lines = lines[:-1]
    else:
        lines = data
    return ''.join(f"{' ' * tab}{_repr_line(line)}\n" for line in lines)


def _format_lines(label: str, data: list[bytes] | bytes | None) -> str:
    return f"{label}:\n" + _format_lines_inner(data)


def _assert_merge(
    result: subprocess.CompletedProcess[bytes],
    expected_lines: list[bytes],
    *,
    under_valgrind: bool = False,
) -> None:
    assert result.returncode == 0, (
        f"Expected exit code 0, got {result.returncode}\n" +
        _format_lines("stderr", result.stderr)
    )
    stdout = result.stdout

    if len(stdout) == 0:
        actual_lines: list[bytes] = []
    else:
        linesep_bytes = os.linesep.encode()
        assert stdout.endswith(linesep_bytes), (
            "Expected stdout to end with a newline\n"
            f"Last line was: " + _repr_line(stdout.split(linesep_bytes)[-1])
        )
        actual_lines = stdout.removesuffix(linesep_bytes).split(linesep_bytes)

    assert actual_lines == expected_lines, (
        "Output mismatch\n" +
        _format_lines(f"Expected {len(expected_lines)} lines", expected_lines) +
        _format_lines(f"But got {len(actual_lines)} lines", actual_lines)
    )

    if not under_valgrind:
        assert len(result.stderr) == 0, (
            "Expected stderr to be empty\n" +
            _format_lines("Got", result.stderr)
        )


def _assert_error(result: subprocess.CompletedProcess[bytes]) -> None:
    assert result.returncode != 0, (
        f"Expected non-zero exit code, got {result.returncode}\n" +
        _format_lines("stdout", result.stdout)
    )
    stderr = result.stderr
    linesep_bytes = os.linesep.encode()

    assert len(stderr) > 0, "Expected an error message on stderr, but it's empty"
    assert stderr.endswith(linesep_bytes), (
        "Expected stderr to end with a newline\n"
        "Last line was: " + _repr_line(stderr.split(linesep_bytes)[-1])
    )


class MergeHarness:
    def __init__(self, run_merge: RunMerge, tmp_path: Path, under_valgrind: bool = False) -> None:
        self._run_merge = run_merge
        self._tmp_path = tmp_path
        self._under_valgrind = under_valgrind

    def file(self, name: str, lines: Sequence[bytes | str], *, sep: bytes | str = '\n') -> Path:
        path = self.path(name)
        _gen_file(path, lines, sep)
        return path

    def path(self, name: str) -> Path:
        return self._tmp_path / name

    def _raw(
        self,
        file_paths: Sequence[str | Path],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[bytes]:
        return self._run_merge(file_paths, **kwargs)

    def ok(
        self,
        file_paths: Sequence[str | Path],
        expected_lines: Sequence[bytes | str],
        **kwargs: Any,
    ) -> None:
        _assert_merge(
            self._raw(file_paths, **kwargs),
            [_to_bytes(line) for line in expected_lines],
            under_valgrind=self._under_valgrind,
        )

    def error(
        self,
        file_paths: Sequence[str | Path],
        **kwargs: Any,
    ) -> None:
        _assert_error(self._raw(file_paths, **kwargs))
