import atexit
from contextlib import contextmanager
from hashlib import sha1
from json import dump, loads, load
from typing import Optional
from functools import partial

# noinspection PyPackageRequirements
from path import Path
from requests import Session, Response, ConnectionError as RConnectionError
# noinspection PyPackageRequirements
from environs import Env


# Do not import library parts here. commons.py should not be loaded
# until LANG is set by test_fa and test_en.


env = Env()
env.read_env()
# Use for updating cache entries
FORCE_OVERWRITE_TESTDATA = env.bool('FORCE_OVERWRITE_TESTDATA', False)
READONLY_TESTDATA = env.bool('READONLY_TESTDATA', True)
REMOVE_UNUSED_TESTDATA = env.bool('REMOVE_UNUSED_TESTDATA', False)

TESTDATA = Path(__file__).parent / 'testdata'

json_dump = partial(
    dump, ensure_ascii=False, check_circular=False, sort_keys=True,
    indent='\t')


class FakeResponse:

    # todo: remove mechanicalsoup stuff
    __slots__ = (
        'content', 'iter_content', 'status_code', 'headers', 'encoding', 'url',
        'soup'  # required by mechanicalsoup
    )

    request = None   # required by mechanicalsoup

    def __init__(
        self, url: str, content: bytes, status_code: int, headers: dict,
        encoding: str
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


def load_response(hsh: str) -> Optional[FakeResponse]:
    filename = f'{hsh}.json'
    try:
        with open(f'{TESTDATA}/{filename}', 'rb') as f:
            d = load(f)
    except FileNotFoundError:
        return None

    if REMOVE_UNUSED_TESTDATA is True:
        USED_TESTDATA.add(filename)

    if 'raise' in d:
        raise RConnectionError('per json data')

    filename = f'{hsh}.html'
    with open(f'{TESTDATA}/{filename}', 'rb') as f:
        content = f.read()

    if REMOVE_UNUSED_TESTDATA is True:
        USED_TESTDATA.add(filename)

    return FakeResponse(
        d['url'], content, d['status_code'], d['headers'], d['encoding'])


def dump_response(hsh, response: Response) -> None:
    d = {
        'status_code': response.status_code,
        # CaseInsensitiveDict is not JSON serializable
        'headers': {**response.headers},
        'encoding': response.encoding,
        'url': response.url}
    with open(f'{TESTDATA}/{hsh}.json', 'w', encoding='utf8') as f:
        json_dump(d, f)
    with open(f'{TESTDATA}/{hsh}.html', 'wb') as f:
        f.write(response.content)


def dump_connection_error(hsh):
    with open(f'{TESTDATA}/{hsh}.json', 'w') as f:
        json_dump({'raise': True}, f)


# noinspection PyDecorator
@staticmethod
def fake_request(method, url, data=None, stream=False, **kwargs):
    if data:
        cache_key = url + repr(sorted(data))
    else:
        cache_key = url
    sha1_hex = sha1(cache_key.encode()).hexdigest()

    if FORCE_OVERWRITE_TESTDATA is True:
        response = None
    else:
        response = load_response(sha1_hex)

    if response is None:  # either FileNotFoundError or FORCE_CACHE_OVERWRITE
        if READONLY_TESTDATA:
            raise RuntimeError(
                f'testdata file not found. '
                f'{READONLY_TESTDATA=} {FORCE_OVERWRITE_TESTDATA=}')
        print('Downloading ' + url)
        with real_request():
            try:
                response = Session().request(
                    method, url, data=data, **kwargs)
            except RConnectionError:
                dump_connection_error(sha1_hex)
        dump_response(sha1_hex, response)

    if stream is True:
        def iter_content(*_):
            # this closure over response will simulate a bound method
            return iter((response.content,))
        response.iter_content = iter_content

    return response


@contextmanager
def real_request():
    Session.request = original_request
    yield
    Session.request = fake_request


original_request = Session.request
Session.request = fake_request


if REMOVE_UNUSED_TESTDATA is True:
    all_testdata_files = {f.name for f in TESTDATA.files()}
    USED_TESTDATA = {*()}

    def rm_unused_files():
        unused_files = (all_testdata_files - USED_TESTDATA)
        for f in unused_files:
            (TESTDATA / f).remove()
        print(f'removed {len(all_testdata_files - USED_TESTDATA)} unused testdata files')

    atexit.register(rm_unused_files)
