from pytest_socket import disable_socket
# noinspection PyPackageRequirements
from environs import Env


env = Env()
env.read_env()
# Use for updating cache entries
FORCE_OVERWRITE_TESTDATA = env.bool('FORCE_OVERWRITE_TESTDATA', False)
READONLY_TESTDATA = env.bool('READONLY_TESTDATA', True)
REMOVE_UNUSED_TESTDATA = env.bool('REMOVE_UNUSED_TESTDATA', False)


if READONLY_TESTDATA:
    disable_socket()
