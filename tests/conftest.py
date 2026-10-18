from contextlib import contextmanager
from functools import partial
from hashlib import sha1
from json import dump, load, loads
from pathlib import Path

from curl_cffi import CurlError, Response
from pytest import Config, Parser, fixture
from pytest_socket import disable_socket

import lib


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup('testdata')

    group.addoption(
        '--force-overwrite-testdata',
        action='store_true',
        help='Regenerate cached test responses.',
    )
    group.addoption(
        '--online',
        action='store_true',
        help='Allow network access during tests.',
    )
    group.addoption(
        '--remove-unused-testdata',
        action='store_true',
        help='Remove unused testdata files after the run.',
    )
    group.addoption(
        '--print-test-filename',
        action='store_true',
        help='Print testdata cache filenames.',
    )


TESTDATA = Path(__file__).parent / 'testdata'

json_dump = partial(
    dump, ensure_ascii=False, check_circular=False, sort_keys=True, indent='\t'
)


def dump_connection_error(hsh, redacted_url):
    with open(f'{TESTDATA}/{hsh}.json', 'w', encoding='utf8') as f:
        json_dump({'raise': True, 'url': redacted_url}, f)


def dump_response(hsh, response: Response, redacted_url: str) -> None:
    d = {
        'status_code': response.status_code,
        # CaseInsensitiveDict is not JSON serializable
        'headers': {**response.headers},
        'encoding': response.encoding,
        'url': redacted_url,
    }
    with open(f'{TESTDATA}/{hsh}.json', 'w', encoding='utf8') as f:
        json_dump(d, f)
    with open(f'{TESTDATA}/{hsh}.html', 'wb') as f:
        f.write(response.content)


class FakeResponse:
    __slots__ = (
        'content',
        'encoding',
        'headers',
        'status_code',
        'url',
    )

    def __init__(
        self,
        url: str,
        content: bytes,
        status_code: int,
        headers: dict,
        encoding: str,
    ):
        self.url = url
        self.content = content
        self.status_code = status_code
        self.encoding = encoding
        self.headers = headers

    def json(self):
        return loads(self.content)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    @property
    def text(self):
        return self.content.decode(self.encoding)

    def iter_content(self):
        yield self.content

    def raise_for_status(self):
        if (self.status_code // 100) != 2:
            raise CurlError('status code was not 2xx')


used_testdata: set[str] = set()


def build_fake_request(config: Config, original_request):
    print_test_filename = config.getoption('--print-test-filename')
    remove_unused_testdata = config.getoption('--remove-unused-testdata')
    force_overwrite_testdata = config.getoption('--force-overwrite-testdata')

    @contextmanager
    def real_request():
        lib.request = original_request
        try:
            yield
        finally:
            lib.request = fake_request  # type: ignore

    def load_response(hsh: str) -> FakeResponse | None:
        if print_test_filename:
            print(f'filename: {hsh}')
        filename = f'{hsh}.json'
        try:
            with open(f'{TESTDATA}/{filename}', 'rb') as f:
                d = load(f)
        except FileNotFoundError:
            return None

        if remove_unused_testdata:
            used_testdata.add(filename)

        if 'raise' in d:
            raise CurlError("per citer's cached testdata")

        filename = f'{hsh}.html'
        with open(f'{TESTDATA}/{filename}', 'rb') as f:
            content = f.read()

        if remove_unused_testdata:
            used_testdata.add(filename)

        return FakeResponse(
            d['url'], content, d['status_code'], d['headers'], d['encoding']
        )

    def fake_request(
        url, *, spoof=False, method: lib.Method = 'GET', stream=False, **kwargs
    ):
        # this import needs to be after Session patch
        from lib.pubmed import NCBI_URL

        redacted_url = url.replace(
            NCBI_URL, NCBI_URL[: NCBI_URL.find('?')] + '?_REDACTED_PARAMS_'
        )

        data: dict | None = kwargs.pop('data', None)
        if data is not None:
            cache_key = redacted_url + repr(sorted(data))
        else:
            cache_key = redacted_url
        sha1_hex = sha1(cache_key.encode()).hexdigest()

        if force_overwrite_testdata:
            response = None
        else:
            response = load_response(sha1_hex)

        if (
            response is None
        ):  # either FileNotFoundError or FORCE_CACHE_OVERWRITE
            print('Downloading ' + url)
            with real_request():
                try:
                    response = lib.request(
                        url, method=method, data=data, spoof=spoof, **kwargs
                    )
                except CurlError:
                    dump_connection_error(sha1_hex, redacted_url)
                    raise
            dump_response(sha1_hex, response, redacted_url)

        response.raise_for_status()
        if stream is True:

            @contextmanager
            def fake_stream():
                yield response

            return fake_stream()

        return response

    return fake_request


def pytest_configure(config: Config) -> None:
    lib.request = build_fake_request(config, lib.request)  # type: ignore

    if not config.getoption('--online'):
        disable_socket()
        from curl_cffi import requests

        requests.Response = requests.Session = NotImplementedError(  # type: ignore
            'No network during dry run. Enable network by --online.'
        )


@fixture(scope='session', autouse=True)
def session_manager(pytestconfig: Config):
    if not pytestconfig.getoption('--remove-unused-testdata'):
        yield
        return
    all_testdata_files = {f.name for f in TESTDATA.iterdir()}
    used_testdata.clear()

    yield

    unused_files = all_testdata_files - used_testdata
    for f in unused_files:
        (TESTDATA / f).unlink()
    print(f'removed {len(unused_files)} unused testdata files')
