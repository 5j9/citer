from sys import argv

from decouple import config
from pytest_socket import disable_socket

# Use for updating cache entries.
FORCE_OVERWRITE_TESTDATA = config('FORCE_OVERWRITE_TESTDATA', False, cast=bool)
READONLY_TESTDATA = config('READONLY_TESTDATA', True, cast=bool)
REMOVE_UNUSED_TESTDATA = len(argv) < 2 and config(
    'REMOVE_UNUSED_TESTDATA', False, cast=bool
)
PRINT_TEST_FILENAME = config('PRINT_TEST_FILENAME', False, cast=bool)


if READONLY_TESTDATA:
    disable_socket()
    from curl_cffi import requests

    requests.Response = requests.Session = NotImplementedError(
        'No network in READONLY_TESTDATA mode'
    )
