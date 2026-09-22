import itertools
import random
from pathlib import Path

import pytest

from helpers import MergeHarness, rand_bytes

_ParameterSet = type(pytest.param())


def _make_param(n_files: int, max_n_strings: int, max_string_length: int) -> _ParameterSet:
    slow_threshold = 4096
    marks = []
    if max_n_strings * max_string_length > slow_threshold:
        marks.append(pytest.mark.slow)

    return pytest.param(n_files, max_n_strings, max_string_length, marks=marks)


def _make_params() -> list[_ParameterSet]:
    files_counts = [1, 2, 3, 5, 10]
    values = [2 ** n for n in range(10)] + [10_000]
    return list(itertools.starmap(_make_param, itertools.product(files_counts, values, values)))


@pytest.mark.parametrize(
    ('n_files', 'max_n_strings', 'max_string_length'),
    _make_params(),
)
def test_random_merge(
    mh: MergeHarness,
    n_files: int,
    max_n_strings: int,
    max_string_length: int,
) -> None:
    seed = hash((85764, n_files, max_n_strings, max_string_length))
    rng = random.Random(seed)

    all_lines: list[bytes] = []
    files: list[Path] = []

    for i in range(n_files):
        n_strings = rng.randint(1, max_n_strings)
        lines = sorted(rand_bytes(max_string_length, rng) for _ in range(n_strings))
        sep = rng.choice([b'\n', b'\r', b'\r\n'])
        f = mh.file(f'input_{i}.txt', lines, sep=sep)
        files.append(f)
        all_lines.extend(lines)

    all_lines.sort()
    mh.ok(files, all_lines)
