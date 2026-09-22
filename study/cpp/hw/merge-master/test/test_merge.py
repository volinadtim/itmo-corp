import itertools
import os
from itertools import chain
from pathlib import Path

import pytest

from helpers import ALL_BYTES_EXCEPT_NEWLINE, MergeHarness, all_strings_of_length


class TestTrivial:
    def test_single_file_single_line(self, mh: MergeHarness) -> None:
        f = mh.file('hi.txt', ['hello'])
        mh.ok([f], ['hello'])

    def test_single_file_multiple_lines(self, mh: MergeHarness) -> None:
        lines = ['alpha', 'beta', 'gamma']
        f = mh.file('greek.txt', lines)
        mh.ok([f], lines)

    def test_two_files_interleaved(self, mh: MergeHarness) -> None:
        f1 = mh.file('interleaved_1.txt', ['aa', 'cc', 'ee'])
        f2 = mh.file('interleaved_2.txt', ['bb', 'dd', 'ff'])
        mh.ok([f1, f2], ['aa', 'bb', 'cc', 'dd', 'ee', 'ff'])

    def test_two_files_one_exhausts_first(self, mh: MergeHarness) -> None:
        f1 = mh.file('exhausting_1.txt', ['bb', 'cc'])
        f2 = mh.file('exhausting_2.txt', ['aa', 'dd', 'ee', 'ff'])
        mh.ok([f1, f2], ['aa', 'bb', 'cc', 'dd', 'ee', 'ff'])

    def test_many_files(self, mh: MergeHarness) -> None:
        line_groups = [
            ['alpha-1', 'alpha-4', 'alpha-7'],
            ['alpha-2', 'alpha-5', 'alpha-8'],
            ['alpha-3', 'alpha-6', 'alpha-9'],
            ['beta-1', 'beta-3', 'beta-6'],
            ['beta-2', 'beta-4', 'beta-7'],
        ]
        files = [
            mh.file(f'f{i}.txt', lines)
            for i, lines in enumerate(line_groups, 1)
        ]
        mh.ok(files, sorted(chain.from_iterable(line_groups)))


class TestOrdering:
    def test_uppercase_sorts_before_lowercase(self, mh: MergeHarness) -> None:
        f1 = mh.file('lower.txt', ['a', 'b'])
        f2 = mh.file('upper.txt', ['A', 'B'])
        mh.ok([f1, f2], ['A', 'B', 'a', 'b'])

    def test_strings_with_spaces(self, mh: MergeHarness) -> None:
        spaces = [' ', '\t']
        lines = [
            ''.join(chars)
            for n in range(4)
            for chars in itertools.product(spaces, repeat=n)
        ]
        files = [
            mh.file(f'spaces_{i}.txt', [line])
            for i, line in enumerate(lines, 1)
        ]
        lines.sort()
        mh.ok(files, lines)

    def test_files_in_reverse_order(self, mh: MergeHarness) -> None:
        f1 = mh.file('rev_1.txt', ['zz'])
        f2 = mh.file('rev_2.txt', ['qq'])
        f3 = mh.file('rev_3.txt', ['aa'])
        mh.ok([f1, f2, f3], ['aa', 'qq', 'zz'])

    def test_same_letter(self, mh: MergeHarness) -> None:
        f1 = mh.file('letter_1.txt', ['a', 'aaa', 'aaaaaa'])
        f2 = mh.file('letter_2.txt', ['aa', 'aaaa', 'aaaaa'])
        mh.ok([f1, f2], ['a', 'aa', 'aaa', 'aaaa', 'aaaaa', 'aaaaaa'])

    def test_common_prefix_1(self, mh: MergeHarness) -> None:
        f1 = mh.file('app_1.txt', ['app', 'apple'])
        f2 = mh.file('app_2.txt', ['apply'])
        f3 = mh.file('app_3.txt', ['applause'])
        mh.ok([f1, f2, f3], ['app', 'applause', 'apple', 'apply'])

    def test_common_prefix_2(self, mh: MergeHarness) -> None:
        f1 = mh.file('ca_1.txt', ['carb', 'care'])
        f2 = mh.file('ca_2.txt', ['car', 'cat'])
        f3 = mh.file('ca_3.txt', ['cab', 'can'])
        mh.ok([f1, f2, f3], ['cab', 'can', 'car', 'carb', 'care', 'cat'])


class TestDuplicates:
    def test_duplicate_strings_within_single_file(self, mh: MergeHarness) -> None:
        f = mh.file('fine.txt', ['this is fine'] * 10)
        mh.ok([f], ['this is fine'] * 10)

    def test_duplicate_strings_across_multiple_files(self, mh: MergeHarness) -> None:
        f1 = mh.file('dup_1.txt', ['aa', 'bb', 'cc', 'cc', 'ee'])
        f2 = mh.file('dup_2.txt', ['aa', 'cc', 'dd'])
        mh.ok([f1, f2], ['aa', 'aa', 'bb', 'cc', 'cc', 'cc', 'dd', 'ee'])

    def test_duplicate_files(self, mh: MergeHarness) -> None:
        f = mh.file('fruits.txt', ['apple', 'banana', 'cherry'])
        mh.ok([f, f, f], ['apple'] * 3 + ['banana'] * 3 + ['cherry'] * 3)

    def test_all_identical_strings(self, mh: MergeHarness) -> None:
        n_files = 5
        files = [
            mh.file(f'dollar_{i}.txt', ['$'] * 3)
            for i in range(1, n_files + 1)
        ]
        mh.ok(files, ['$'] * (n_files * 3))

    def test_duplicates_and_prefixes(self, mh: MergeHarness) -> None:
        f1 = mh.file('dupr_1.txt', ['a', 'aa', 'ab', 'aba', 'b'])
        f2 = mh.file('dupr_2.txt', ['a', 'aa', 'aaa', 'ab', 'abb', 'ba'])
        f3 = mh.file('dupr_3.txt', ['a', 'ab', 'aba', 'abc', 'baa'])
        f4 = mh.file('dupr_4.txt', ['abc'])
        mh.ok([f1, f2, f3, f4], [
            'a', 'a', 'a', 'aa', 'aa', 'aaa', 'ab', 'ab', 'ab',
            'aba', 'aba', 'abb', 'abc', 'abc', 'b', 'ba', 'baa',
        ])


class TestEmptyFiles:
    def test_single_empty_file(self, mh: MergeHarness) -> None:
        f = mh.file('empty.txt', [])
        mh.ok([f], [])

    def test_multiple_empty_files(self, mh: MergeHarness) -> None:
        f1 = mh.file('empty_1.txt', [])
        f2 = mh.file('empty_2.txt', [])
        f3 = mh.file('empty_3.txt', [])
        mh.ok([f1, f2, f3], [])

    def test_empty_and_non_empty_files(self, mh: MergeHarness) -> None:
        f1 = mh.file('f1.txt', ['aa', 'ff'])
        f2 = mh.file('f2.txt', [])
        f3 = mh.file('f3.txt', ['cc'])
        f4 = mh.file('f4.txt', ['bb', 'dd', 'ee'])
        f5 = mh.file('f5.txt', [])
        mh.ok([f1, f2, f3, f4, f5], ['aa', 'bb', 'cc', 'dd', 'ee', 'ff'])


class TestEmptyLines:
    def test_single_empty_line(self, mh: MergeHarness) -> None:
        f = mh.file('single_empty_line.txt', [''])
        mh.ok([f], [''])

    def test_multiple_empty_lines(self, mh: MergeHarness) -> None:
        f = mh.file('empty_lines.txt', ['', '', ''])
        mh.ok([f], ['', '', ''])

    def test_empty_lines_in_multiple_files(self, mh: MergeHarness) -> None:
        n_files = 3
        files: list[Path] = []
        all_lines: list[str] = []
        for i in range(1, n_files + 1):
            lines = [''] * i
            f = mh.file(f'empty_lines_{i}.txt', lines)
            files.append(f)
            all_lines.extend(lines)
        all_lines.sort()
        mh.ok(files, all_lines)

    def test_empty_lines_before_non_empty_in_single_file(self, mh: MergeHarness) -> None:
        f = mh.file('empty_before_hello.txt', ['', '', 'hello'])
        mh.ok([f], ['', '', 'hello'])

    def test_empty_lines_before_non_empty_in_multiple_files(self, mh: MergeHarness) -> None:
        n_files = 3
        files: list[Path] = []
        all_lines: list[str] = []
        for i in range(1, n_files + 1):
            lines = [''] * i + [f'hello {i}']
            f = mh.file(f'empty_before_hello_{i}.txt', lines)
            files.append(f)
            all_lines.extend(lines)
        all_lines.sort()
        mh.ok(files, all_lines)


SEPS = ['\n', '\r', '\r\n']


class TestLineSeparators:
    @pytest.mark.parametrize('sep', SEPS)
    def test_single_file_single_line(self, mh: MergeHarness, sep: str) -> None:
        f = mh.file('hi.txt', ['hello'], sep=sep)
        mh.ok([f], ['hello'])

    @pytest.mark.parametrize('sep', SEPS)
    def test_single_file_multiple_lines(self, mh: MergeHarness, sep: str) -> None:
        lines = ['alpha', 'beta', 'gamma']
        f = mh.file('greek.txt', lines, sep=sep)
        mh.ok([f], lines)

    @pytest.mark.parametrize('sep', SEPS)
    def test_multiple_files(self, mh: MergeHarness, sep: str) -> None:
        f1 = mh.file('f1.txt', ['aa', 'cc', 'dd'], sep=sep)
        f2 = mh.file('f2.txt', ['bb', 'ee', 'ff'], sep=sep)
        mh.ok([f1, f2], ['aa', 'bb', 'cc', 'dd', 'ee', 'ff'])

    @pytest.mark.parametrize('sep1', SEPS)
    @pytest.mark.parametrize('sep2', SEPS)
    def test_mixed_separators_across_files(self, mh: MergeHarness, sep1: str, sep2: str) -> None:
        f1 = mh.file('f1.txt', ['aa', 'cc', 'dd'], sep=sep1)
        f2 = mh.file('f2.txt', ['bb', 'ee', 'ff'], sep=sep2)
        mh.ok([f1, f2], ['aa', 'bb', 'cc', 'dd', 'ee', 'ff'])

    @pytest.mark.parametrize('sep_seq', [
        sep_seq
        for n in range(4)
        for sep_seq in itertools.product(SEPS, repeat=n)
    ])
    def test_empty_lines(self, mh: MergeHarness, sep_seq: list[str]) -> None:
        content = ''.join(sep_seq)
        n_lines = len(content.replace('\r\n', '\n'))
        f = mh.file('empty_lines.txt', [content], sep='')
        mh.ok([f], [''] * n_lines)

    def test_no_trailing_separator(self, mh: MergeHarness) -> None:
        lines = ['cat', 'dog', 'goat']
        content = '\n'.join(lines)
        f = mh.file('no_trail.txt', [content], sep='')
        mh.ok([f], lines)


class TestBinaryData:
    def test_null_bytes_single_file(self, mh: MergeHarness) -> None:
        lines = ['\0', '\0\0', 'a\0b', 'a\0c', 'a\0c\0', 'abc', 'abc\0']
        f = mh.file('nulls.txt', lines)
        mh.ok([f], lines)

    def test_null_bytes_multiple_files(self, mh: MergeHarness) -> None:
        f1 = mh.file('nulls_1.txt', ['\0', 'a\0b', 'abc\0'])
        f2 = mh.file('nulls_2.txt', ['\0\0', 'a\0c', 'a\0c\0'])
        f3 = mh.file('nulls_3.txt', ['abc'])
        mh.ok([f1, f2, f3], ['\0', '\0\0', 'a\0b', 'a\0c', 'a\0c\0', 'abc', 'abc\0'])

    def test_all_byte_values(self, mh: MergeHarness) -> None:
        lines = [bytes([b]) for b in ALL_BYTES_EXCEPT_NEWLINE]
        n_files = 5
        files = [
            mh.file(f'bytes_{i + 1}.txt', lines[i::n_files])
            for i in range(n_files)
        ]
        mh.ok(files, lines)

    def test_unicode(self, mh: MergeHarness) -> None:
        f1 = mh.file('fruits_1.txt', ['апельсин', 'банан', 'мандарин'])
        f2 = mh.file('fruits_2.txt', ['ананас', 'груша', 'манго'])
        f3 = mh.file('fruits_3.txt', ['гранат', 'яблоко'])
        mh.ok(
            [f1, f2, f3],
            ['ананас', 'апельсин', 'банан', 'гранат', 'груша', 'манго', 'мандарин', 'яблоко']
        )


@pytest.mark.slow
class TestBigData:
    @pytest.mark.skipif(
        os.name == 'nt',
        reason="Windows has a hard limit on command length",
    )
    def test_many_files(self, mh: MergeHarness) -> None:
        n_files = 1000
        files = [
            mh.file(f'{i:03d}.txt', [f'{i:03d}'])
            for i in range(n_files)
        ]
        expected = [f'{i:03d}' for i in range(n_files)]
        mh.ok(files, expected)

    def test_many_lines(self, mh: MergeHarness) -> None:
        lines_1 = all_strings_of_length(3)
        lines_2 = all_strings_of_length(4)
        f1 = mh.file('big_1.txt', lines_1)
        f2 = mh.file('big_2.txt', lines_2)
        mh.ok([f1, f2], sorted(lines_1 + lines_2))

    def test_long_lines(self, mh: MergeHarness) -> None:
        line_a = 'a' * 100_000
        line_b = 'b' * 100_000
        line_c = 'c' * 10_000_000
        line_d = 'd' * 10_000_000
        f1 = mh.file('long_1.txt', [line_a, line_d])
        f2 = mh.file('long_2.txt', [line_b, line_c])
        mh.ok([f1, f2], [line_a, line_b, line_c, line_d])


class TestErroneous:
    def test_no_arguments(self, mh: MergeHarness) -> None:
        mh.error([])

    def test_nonexistent_file(self, mh: MergeHarness) -> None:
        mh.error([mh.path('missing.txt')])

    def test_multiple_nonexistent_files(self, mh: MergeHarness) -> None:
        mh.error([
            mh.path('missing_1.txt'),
            mh.path('missing_2.txt'),
        ])

    def test_nonexistent_among_valid(self, mh: MergeHarness) -> None:
        f1 = mh.file('valid_1.txt', ['aaa'])
        f2 = mh.path('missing.txt')
        f3 = mh.file('valid_2.txt', ['bbb'])
        mh.error([f1, f2, f3])

    @pytest.mark.skipif(
        os.name == 'nt',
        reason="Windows has limited control of file permissions",
    )
    def test_protected(self, mh: MergeHarness) -> None:
        f = mh.file('secret.txt', ['Pa$$w0rd'])
        f.chmod(0o000)
        mh.error([f])

    @pytest.mark.skipif(
        os.name == 'nt',
        reason="Windows has limited control of file permissions",
    )
    def test_protected_among_valid(self, mh: MergeHarness) -> None:
        f1 = mh.file('f1.txt', ['aaa'])
        f2 = mh.file('f2_secret.txt', ['bbb'])
        f3 = mh.file('f3.txt', ['ccc'])
        f2.chmod(0o000)
        mh.error([f1, f2, f3])

    def test_directory_as_file(self, mh: MergeHarness) -> None:
        d = mh.path('some-dir')
        d.mkdir()
        mh.error([d])

    @pytest.mark.skipif(
        not Path('/dev/full').exists(),
        reason="/dev/full not available",
    )
    def test_stdout_write_failure(self, mh: MergeHarness) -> None:
        lines = ['x' * i for i in range(100)]
        f = mh.file('big.txt', lines)
        with open('/dev/full', 'wb') as devfull:
            mh.error([f], stdout=devfull)

    def test_unsorted_single_file(self, mh: MergeHarness) -> None:
        f = mh.file('unsorted.txt', ['delta', 'gamma', 'alpha', 'beta'])
        mh.error([f])

    def test_unsorted_empty_line(self, mh: MergeHarness) -> None:
        f = mh.file('unsorted_with_empty.txt', ['aa', 'bb', ''])
        mh.error([f])

    def test_unsorted_prefix(self, mh: MergeHarness) -> None:
        f = mh.file('unsorted_prefix.txt', ['apple', 'app'])
        mh.error([f])

    def test_unsorted_among_sorted(self, mh: MergeHarness) -> None:
        f1 = mh.file('sorted_1.txt', ['Earth', 'Uranus'])
        f2 = mh.file('sorted_2.txt', ['Jupiter', 'Venus'])
        f3 = mh.file('unsorted.txt', ['Mercury', 'Mars'])
        mh.error([f1, f2, f3])
