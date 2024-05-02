#!/usr/bin/env python3
"""A script to be run as part of forgetools/install_python_webservice.py."""

import os
from os import O_CREAT, O_EXCL, O_WRONLY, chmod, close, open as os_open
from os.path import expanduser
from re import sub
from subprocess import check_output

HOME = expanduser('~')


def set_file_permissions():
    try:
        chmod(HOME + '/www/python/src/citer.log', 0o660)
    except FileNotFoundError:
        close(
            os_open(
                HOME + '/www/python/src/citer.log',
                O_CREAT | O_EXCL | O_WRONLY,
                0o660,
            )
        )
    chmod(HOME + '/www/python/src/config.py', 0o660)


def write_uwsgi_ini():
    with open(HOME + '/www/python/uwsgi.ini', 'wb') as f:
        f.write(b'[uwsgi]\nenable-threads = true\n')


def copy_config():
    committer_date = (
        check_output(
            [
                'git',
                '-C',
                HOME + '/www/python/src',
                'log',
                '-1',
                '--format=%cd',
                '--date=short',
            ]
        )
        .rstrip()
        .replace(b'-', b'.')
    )

    def opener(path, flags):
        return os.open(path, flags, 0o660)

    with open(HOME + '/.citer_config', 'rb') as home_config:
        with open(
            HOME + '/www/python/src/config.py', 'wb', opener=opener
        ) as src_config:
            src_config.write(
                sub(
                    b"(USER_AGENT = '.*)'\n",
                    rb'\1 v' + committer_date + b"'\n",
                    home_config.read(),
                    1,
                )
            )


def main():
    copy_config()
    write_uwsgi_ini()
    set_file_permissions()


if __name__ == '__main__':
    main()
