from pytest_socket import disable_socket
# noinspection PyPackageRequirements
from decouple import config


# Use for updating cache entries
FORCE_OVERWRITE_TESTDATA = config('FORCE_OVERWRITE_TESTDATA', False, cast=bool)
READONLY_TESTDATA = config('READONLY_TESTDATA', True, cast=bool)
REMOVE_UNUSED_TESTDATA = config('REMOVE_UNUSED_TESTDATA', False, cast=bool)


if READONLY_TESTDATA:
    disable_socket()
