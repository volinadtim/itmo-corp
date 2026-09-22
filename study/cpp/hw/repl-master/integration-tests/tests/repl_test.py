import itertools
import random
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from types import TracebackType
from typing import Optional, Type

import pytest

from tests.error_registry import error_registry

DEFAULT_RPC_HOST = '158.160.41.77'
DEFAULT_RPC_PORT = 5050

ERROR_PREFIX = 'Error: '

app_exe_path = None


class ReplExitResult:
    def __init__(self, exit_code: int, stdout: str, stderr: str):
        self.exit_code = exit_code
        self.stdout = stdout.rstrip()
        self.stderr = stderr.rstrip()

    def assert_success(self) -> None:
        assert self.exit_code == 0, self.stderr
        assert self.stderr == ''

    def assert_error(self, what: str) -> None:
        assert self.exit_code != 0
        assert self.stdout == ''
        assert self.stderr.startswith(ERROR_PREFIX)
        error_registry.register(what, self.stderr.removeprefix(ERROR_PREFIX))


class ReplQueryResult:
    def __init__(self, stdout: str):
        if stdout.startswith(ERROR_PREFIX):
            self.text = stdout.removeprefix(ERROR_PREFIX).rstrip()
            self.is_ok = False
        else:
            self.text = stdout.rstrip()
            self.is_ok = True

    def assert_result(self, expected: str) -> None:
        assert self.is_ok, self.text
        assert self.text == expected

    def assert_error(self, what: str) -> None:
        assert not self.is_ok
        error_registry.register(what, self.text)


class SchemaProvider(ABC):
    @abstractmethod
    def schema_path(self) -> Path:
        pass

    @abstractmethod
    def rpc_path(self) -> str:
        pass


class SchemaByName(SchemaProvider):
    def __init__(self, name: str):
        self._schema_name = name

    def schema_path(self) -> Path:
        current_script_dir = Path(__file__).resolve().parent
        integration_tests_root_dir = current_script_dir.parent
        schemas_dir = integration_tests_root_dir / 'schemas'
        return schemas_dir / f'{self._schema_name}.sc'

    def rpc_path(self) -> str:
        return self._schema_name


class SchemaByContent(SchemaProvider):
    def __init__(self, content: str, rpc_path: str):
        self._schema_file = tempfile.NamedTemporaryFile(mode='w+')
        self._schema_file.write(content + '\n')
        self._schema_file.flush()
        self._rpc_path = rpc_path

    def schema_path(self) -> Path:
        return Path(self._schema_file.name)

    def rpc_path(self) -> str:
        return self._rpc_path

    def __enter__(self) -> 'SchemaByContent':
        self._schema_file.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        self._schema_file.__exit__(exc_type, exc_val, exc_tb)


class Repl:
    def __init__(
        self,
        post_args: list[str] = None,
        pre_args: list[str] = None,
        *,
        schema: str | SchemaProvider = None,
        rpc_host: str = DEFAULT_RPC_HOST,
        rpc_port: int = DEFAULT_RPC_PORT,
        no_tty: bool = True
    ):
        global app_exe_path
        command = [str(app_exe_path)]

        if pre_args is not None:
            command.extend(pre_args)
        if schema is not None:
            schema_provider = schema if isinstance(schema, SchemaProvider) else SchemaByName(schema)
            command.extend(['--schema', str(schema_provider.schema_path())])
            command.extend(['--rpc-host', rpc_host])
            command.extend(['--rpc-port', str(rpc_port)])
            command.extend(['--rpc-path', schema_provider.rpc_path()])
        if no_tty:
            command.append('--no-tty')
        if post_args is not None:
            command.extend(post_args)

        self._process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        assert self._process.stdin is not None, "Failed to open STDIN"
        assert self._process.stdout is not None, "Failed to open STDOUT"
        assert self._process.stderr is not None, "Failed to open STDERR"

    def query(self, query_line: str) -> ReplQueryResult:
        self._process.stdin.write(query_line + '\n')
        self._process.stdin.flush()
        result_line = self._process.stdout.readline()
        return ReplQueryResult(result_line)

    def exit(self, timeout=0.5) -> ReplExitResult:
        self._process.stdin.close()
        return self.wait_for_exit(timeout)

    def wait_for_exit(self, timeout=0.5) -> ReplExitResult:
        exit_code = self._process.wait(timeout)
        stdout = self._process.stdout.read()
        stderr = self._process.stderr.read()
        return ReplExitResult(exit_code, stdout, stderr)

    def __enter__(self) -> 'Repl':
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        exit_result = self.exit()
        if exc_type is None:
            exit_result.assert_success()

    @staticmethod
    def run(*args, timeout=0.5, **kwargs) -> ReplExitResult:
        return Repl(*args, **kwargs).exit(timeout)


def interleave_random_whitespaces(
    tokens: list[str],
    whitespace_chars: list[str],
    max_ws_len: int = 2
) -> str:
    def random_whitespace() -> str:
        return ''.join(random.choices(whitespace_chars, k=random.randint(0, max_ws_len)))

    whitespaces = [random_whitespace() for _ in range(len(tokens) + 1)]
    interleaved = itertools.chain.from_iterable(
        itertools.zip_longest(whitespaces, tokens, fillvalue='')
    )
    return ''.join(interleaved)


class TestCommandArguments:
    @property
    def valid_schema_name(self) -> str:
        return 'person'

    @property
    def valid_schema_path(self) -> str:
        return str(SchemaByName(self.valid_schema_name).schema_path())

    def test_no_schema(self) -> None:
        Repl.run([]).assert_error("No schema arg")

    def test_invalid_use_of_schema_arg(self) -> None:
        Repl.run(['--schema']).assert_error("--schema without value")
        Repl.run([self.valid_schema_path, '--schema']).assert_error("Schema path before --schema")

    def test_schema_does_not_exist(self) -> None:
        Repl.run(['--schema', 'wrong']).assert_error("Schema does not exist (space)")
        Repl.run(['--schema=wrong']).assert_error("Schema does not exist (=)")

        Repl.run(['--schema', '']).assert_error("Empty schema path (space)")
        Repl.run(['--schema=']).assert_error("Empty schema path (=)")

    def test_invalid_args(self) -> None:
        Repl.run(['--schemaaa', self.valid_schema_path]).assert_error("--schemaaa")
        Repl.run([self.valid_schema_path]).assert_error("Schema path without --schema")

        Repl.run(schema=self.valid_schema_name, pre_args=['1111']).assert_error("'1111' at the beginning")
        Repl.run(schema=self.valid_schema_name, post_args=['1111']).assert_error("'1111' at the end")

        Repl.run(schema=self.valid_schema_name, pre_args=['--no-ttyt']).assert_error("'--no-ttyt' at the beginning")
        Repl.run(schema=self.valid_schema_name, post_args=['--no-ttyt']).assert_error("'--no-ttyt' at the end")

    def test_correct_args(self) -> None:
        Repl.run(schema=self.valid_schema_name).assert_success()


class TestSchemaParsing:
    def test_person_schema(self) -> None:
        with Repl(schema='person') as repl:
            repl.query('getId(person={id=200, name="Egor", email="cool@gmail.com"})').assert_result('200')
            repl.query('getId(person={id=225, name="Egor", email="cool@gmail.com"})').assert_result('225')
            repl.query('getName(person={id=225, name="Egor", email="cool@gmail.com"})').assert_result('"Egor"')

    def test_person_and_concat_schema(self) -> None:
        with Repl(schema='person-and-concat') as repl:
            repl.query('getId(person={id=200, name="Egor", email="cool@gmail.com"})').assert_result('200')
            repl.query('getId(person={id=225, name="Egor", email="cool@gmail.com"})').assert_result('225')
            repl.query('getName(person={id=225, name="Egor", email="cool@gmail.com"})').assert_result('"Egor"')
            repl.query('concat(left="hello, ", right="world!")').assert_result('"hello, world!"')
            repl.query('concat(left="", right="empty")').assert_result('"empty"')

    def test_empty_file(self) -> None:
        Repl.run(schema='empty').assert_success()

    def test_nested(self) -> None:
        with Repl(schema='shop') as repl:
            repl.query('getProduct(item={product={id=35}, quantity=2})').assert_result('Product{id=35}')

    INLINE_SCHEMA_TOKENS: list[str] = [
        'struct', ' Person', '{', 'int32', ' id', ';', 'string', ' name', ';', 'string', ' email', ';', '}',
        'fn', ' getId', '->', 'int32', '{', 'Person', ' person', ';', '}'
    ]

    def test_no_extra_whitespaces(self) -> None:
        schema_content = ''.join(TestSchemaParsing.INLINE_SCHEMA_TOKENS)

        with SchemaByContent(schema_content, 'person') as schema:
            with Repl(schema=schema) as repl:
                repl.query('getId(person={id=200, name="Egor", email="cool@gmail.com"})').assert_result('200')

    @pytest.mark.parametrize('rand_seed', range(1337, 1337 + 10))
    def test_random_whitespaces(self, rand_seed: int) -> None:
        random.seed(rand_seed)
        schema_content = interleave_random_whitespaces(
            TestSchemaParsing.INLINE_SCHEMA_TOKENS,
            [' ', '\t', '\n']
        )

        with SchemaByContent(schema_content, 'person') as schema:
            with Repl(schema=schema) as repl:
                repl.query('getId(person={id=200, name="Egor", email="cool@gmail.com"})').assert_result('200')

    @pytest.mark.parametrize('token_idx', range(len(INLINE_SCHEMA_TOKENS)))
    def test_missing_token(self, token_idx: int) -> None:
        unfiltered_tokens = TestSchemaParsing.INLINE_SCHEMA_TOKENS
        dropped_token = unfiltered_tokens[token_idx].strip()
        filtered_tokens = unfiltered_tokens[:token_idx] + unfiltered_tokens[(token_idx + 1):]
        schema_content = ' '.join(filtered_tokens)

        with SchemaByContent(schema_content, 'person') as schema:
            Repl.run(schema=schema).assert_error(f"Missing schema token #{token_idx} ('{dropped_token}')")

    def test_incorrect_keyword(self) -> None:
        Repl.run(schema='bad-invalid-keyword').assert_error("Invalid keyword in schema")

    def test_recursive_struct(self) -> None:
        Repl.run(schema='bad-recursive-struct').assert_error("Recursive struct")

    def test_function_as_type(self) -> None:
        Repl.run(schema='bad-function-as-type').assert_error("Function used as a type")

    def test_duplicate_function_name(self) -> None:
        Repl.run(schema='bad-duplicate-function-name').assert_error("Duplicate function name")

    def test_duplicate_struct_name(self) -> None:
        Repl.run(schema='bad-duplicate-struct-name').assert_error("Duplicate struct name")

    def test_duplicate_struct_field(self) -> None:
        Repl.run(schema='bad-duplicate-struct-field').assert_error("Duplicate struct field")

    def test_duplicate_function_argument(self) -> None:
        Repl.run(schema='bad-duplicate-function-argument').assert_error("Duplicate function argument")

    def test_same_name_for_function_and_struct(self) -> None:
        Repl.run(schema='bad-same-name-for-function-and-struct').assert_error("Same name for function and struct")

    def test_function_name_hash_collision(self) -> None:
        Repl.run(schema='bad-function-name-hash-collision').assert_error("Function name hash collision")


class TestQueries:
    QUERY_TOKENS: list[str] = [
        'getId', '(', 'person', '=', '{', 'id', '=', '200', ',',
        'name', '=', '"Egor"', ',' 'email' '=', '"cool@gmail.com"', '}', ')'
    ]

    def test_no_extra_whitespaces(self) -> None:
        query = ''.join(TestQueries.QUERY_TOKENS)
        with Repl(schema='person') as repl:
            repl.query(query).assert_result('200')

    def test_random_whitespaces(self) -> None:
        random.seed(1337)
        with Repl(schema='person') as repl:
            for _ in range(10):
                query = interleave_random_whitespaces(TestQueries.QUERY_TOKENS, [' ', '\t'])
                repl.query(query).assert_result('200')

    def test_incorrect_function_name(self) -> None:
        with Repl(schema='person') as repl:
            repl.query('nonExistingFunction()').assert_error("Non-existing function")
            repl.query('()').assert_error("Empty function name (no args)")
            repl.query('(id=200)').assert_error("Empty function name (with args)")
            repl.query('get Id(person={id=200, name="Egor", email="cool').assert_error("Function name contains space")

    def test_incorrect_arguments(self) -> None:
        with Repl(schema='person') as repl:
            repl.query('getId(personn={id=200, name="Egor", email="cool@gmail.com"})').assert_error("Invalid arg name")
            repl.query('getId(person={id=200, name="Egor", email=cool@gmail.com})').assert_error("Unquoted string")
            repl.query('getId({id=200, name="Egor", email=cool@gmail.com})').assert_error("No function arg name")
            repl.query('getId(person={id=200, "Egor", email=cool@gmail.com})').assert_error("No struct arg name")
            repl.query('getId(person={id=200, name="Egor"})').assert_error("Missing argument")

    def test_duplicate_arguments(self) -> None:
        with Repl(schema='person-and-concat') as repl:
            repl.query('concat(left="a", left="b", right="c")').assert_error("Duplicate function argument (left)")
            repl.query('concat(left="a", right="b", right="c")').assert_error("Duplicate function argument (right)")
            repl.query('getId(person={id=1, id=2, name="Egor", email="x"})').assert_error("Duplicate struct field (id)")
            repl.query('getId(person={id=1, name="Egor", email="x", name="Ivan"})').assert_error(
                "Duplicate struct field (name)"
            )

    def test_missing_token(self) -> None:
        unfiltered_tokens = TestQueries.QUERY_TOKENS

        with Repl(schema='person') as repl:
            for token_idx in range(len(unfiltered_tokens)):
                dropped_token = unfiltered_tokens[token_idx]
                filtered_tokens = unfiltered_tokens[:token_idx] + unfiltered_tokens[(token_idx + 1):]
                query = ' '.join(filtered_tokens)
                repl.query(query).assert_error(f"Missing query token #{token_idx} ('{dropped_token}')")

    def test_function_without_arguments(self) -> None:
        with Repl(schema='numbers') as repl:
            repl.query('getSomeNumber()').assert_result('42')

    def test_nested(self) -> None:
        with Repl(schema='shop') as repl:
            repl.query('getProduct(item={product={id=35}, quantity=2})').assert_result('Product{id=35}')
            repl.query('getQuantity(item={product={id=35}, quantity=2})').assert_result('2')
            repl.query(
                'addItemsToOrder(order={item={product={id=35}, quantity=2}, id=99}, quantity=3)'
            ).assert_result(
                'Order{id=99, item=OrderItem{product=Product{id=35}, quantity=5}}'
            )

    def test_optional_struct_name(self) -> None:
        with Repl(schema='shop') as repl:
            repl.query('getProduct(item=OrderItem{product={id=35}, quantity=2})').assert_result('Product{id=35}')
            repl.query('getProduct(item={product=Product{id=35}, quantity=2})').assert_result('Product{id=35}')
            repl.query('getProduct(item=OrderItem{product=Product{id=35}, quantity=2})').assert_result('Product{id=35}')


class TestTypes:
    def test_int32(self) -> None:
        with Repl(schema='person') as repl:
            repl.query('getId(person={id=2147483648, name="Egor", email="cool"})').assert_error('int32 overflow')
            repl.query('getId(person={id=-2147483649, name="Egor", email="cool"})').assert_error('int32 underflow')
            repl.query('getId(person={id=2147483647, name="Egor", email="cool"})').assert_result('2147483647')
            repl.query('getId(person={id=-2147483648, name="Egor", email="cool"})').assert_result('-2147483648')

    def test_int64(self) -> None:
        with Repl(schema='point') as repl:
            repl.query('getX(p={x=9223372036854775808, y=10})').assert_error('int64 overflow')
            repl.query('getX(p={x=-9223372036854775809, y=10})').assert_error('int64 underflow')
            repl.query('getX(p={x=9223372036854775807, y=10})').assert_result('9223372036854775807')
            repl.query('getX(p={x=-9223372036854775808, y=10})').assert_result('-9223372036854775808')

    def test_uint32(self) -> None:
        with Repl(schema='car') as repl:
            repl.query('getCarId(car={id=4294967296, price=0})').assert_error('uint32 overflow')
            repl.query('getCarId(car={id=-1, price=0})').assert_error('uint32 underflow')
            repl.query('getCarId(car={id=4294967295, price=0})').assert_result('4294967295')
            repl.query('getCarId(car={id=0, price=0})').assert_result('0')

    def test_uint64(self) -> None:
        with Repl(schema='car') as repl:
            repl.query('getCarPrice(car={id=0, price=18446744073709551616})').assert_error('uint64 overflow')
            repl.query('getCarPrice(car={id=0, price=-1})').assert_error('uint64 underflow')
            repl.query('getCarPrice(car={id=0, price=18446744073709551615})').assert_result('18446744073709551615')
            repl.query('getCarPrice(car={id=0, price=0})').assert_result('0')


class TestRPC:
    def test_server_error(self) -> None:
        with Repl(schema='numbers') as repl:
            repl.query('square(a=123456789)').assert_error('Server error (square overflow)')
            repl.query('square(a=21)').assert_result('441')

    def test_connection_error(self) -> None:
        repl = Repl(schema='numbers', rpc_host='1.1.1.1', rpc_port=1234)
        query_result = repl.query('square(a=21)')
        exit_result = repl.exit()
        if exit_result.exit_code == 0:
            query_result.assert_error('Connection error')
        else:
            exit_result.assert_error('Connection error')

    def test_invalid_host(self) -> None:
        repl = Repl(schema='numbers', rpc_host='255.0.256.257', rpc_port=0)
        query_result = repl.query('square(a=21)')
        exit_result = repl.exit()
        if exit_result.exit_code == 0:
            query_result.assert_error('Invalid host')
            exit_result.assert_success()
        else:
            exit_result.assert_error('Invalid host')
