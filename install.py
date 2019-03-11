#!/usr/bin/env python3
"""A script to be run as part of forgetools/install_python_webservice.py."""

from os import chmod, open as os_open, close, O_CREAT, O_WRONLY, O_EXCL
from os.path import expanduser


HOME = expanduser('~')


def set_file_permissions():
    try:
        chmod(HOME + '/www/python/src/citer.log', 0o660)
    except FileNotFoundError:
        close(os_open(
            HOME + '/www/python/src/citer.log',
            O_CREAT | O_EXCL | O_WRONLY,
            0o660))
    chmod(HOME + '/www/python/src/config.py', 0o660)


def copy_config():
    with open(HOME + '/.config.py', 'r') as home_config:
        with open(HOME + '/www/python/src/config.py', 'w') as src_config:
            src_config.write(home_config.read())


def main():
    set_file_permissions()
    copy_config()


if __name__ == '__main__':
    main()
