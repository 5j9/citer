# noinspection PyPackageRequirements
from decouple import config
from pytest_socket import disable_socket

# Use for updating cache entries
FORCE_OVERWRITE_TESTDATA = config('FORCE_OVERWRITE_TESTDATA', False, cast=bool)
READONLY_TESTDATA = config('READONLY_TESTDATA', True, cast=bool)
REMOVE_UNUSED_TESTDATA = config('REMOVE_UNUSED_TESTDATA', False, cast=bool)
PRINT_TEST_FILENAME = config('PRINT_TEST_FILENAME', False, cast=bool)


if READONLY_TESTDATA:
    disable_socket()
