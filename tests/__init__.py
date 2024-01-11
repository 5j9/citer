import atexit
from contextlib import contextmanager
from functools import partial
from hashlib import sha1
from json import dump, load, loads
from pathlib import Path

from httpx import ConnectError, HTTPError, Response

from lib import commons
from tests.conftest import FORCE_OVERWRITE_TESTDATA, REMOVE_UNUSED_TESTDATA

# Do not import library parts here. commons.py should not be loaded
# until LANG is set by test_fa and test_en.

TESTDATA = Path(__file__).parent / 'testdata'

json_dump = partial(
    dump, ensure_ascii=False, check_circular=False, sort_keys=True, indent='\t'
)


class FakeResponse:
    __slots__ = (
        'content',
        'status_code',
        'headers',
        'encoding',
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

    def iter_bytes(self, _):
        yield self.content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPError


def load_response(hsh: str) -> FakeResponse | None:
    filename = f'{hsh}.json'
    try:
        with open(f'{TESTDATA}/{filename}', 'rb') as f:
            d = load(f)
    except FileNotFoundError:
        return None

    if REMOVE_UNUSED_TESTDATA is True:
        USED_TESTDATA.add(filename)

    if 'raise' in d:
        raise ConnectError('per json data')

    filename = f'{hsh}.html'
    with open(f'{TESTDATA}/{filename}', 'rb') as f:
        content = f.read()

    if REMOVE_UNUSED_TESTDATA is True:
        USED_TESTDATA.add(filename)

    return FakeResponse(
        d['url'], content, d['status_code'], d['headers'], d['encoding']
    )


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


def dump_connection_error(hsh):
    with open(f'{TESTDATA}/{hsh}.json', 'w') as f:
        json_dump({'raise': True}, f)


# noinspection PyDecorator
@staticmethod
def fake_request(url, spoof=False, method='get', stream=False, **kwargs):
    if url.startswith(NCBI_URL):
        redacted_url = url.replace(
            NCBI_URL, NCBI_URL[: NCBI_URL.find('?')] + '?_REDACTED_PARAMS_'
        )
    else:
        redacted_url = url

    data: dict | None = kwargs.pop('data', None)
    if data is not None:
        cache_key = redacted_url + repr(sorted(data))
    else:
        cache_key = redacted_url
    sha1_hex = sha1(cache_key.encode()).hexdigest()

    if FORCE_OVERWRITE_TESTDATA is True:
        response = None
    else:
        response = load_response(sha1_hex)

    if response is None:  # either FileNotFoundError or FORCE_CACHE_OVERWRITE
        print('Downloading ' + url)
        with real_request():
            try:
                response = commons.request(
                    url, method=method, data=data, spoof=spoof, **kwargs
                )
            except ConnectError:
                dump_connection_error(sha1_hex)
        dump_response(sha1_hex, response, redacted_url)

    return response


@contextmanager
def real_request():
    commons.request = original_request
    yield
    commons.request = fake_request


original_request = commons.request
commons.request = fake_request

# this import needs to placed after Session patch
from lib.pubmed import NCBI_URL  # noqa

if REMOVE_UNUSED_TESTDATA is True:
    all_testdata_files = {f.name for f in TESTDATA.iterdir()}
    USED_TESTDATA = {*()}

    def rm_unused_files():
        unused_files = all_testdata_files - USED_TESTDATA
        for f in unused_files:
            (TESTDATA / f).unlink()
        print(
            f'removed {len(all_testdata_files - USED_TESTDATA)} unused testdata files'
        )

    atexit.register(rm_unused_files)
