#!/usr/bin/env python3
"""A script to be run as part of forgetools/install_python_webservice.py."""

from os import O_CREAT, O_EXCL, O_WRONLY, chmod, close, open as os_open
from pathlib import Path
from re import sub
from subprocess import check_output

HOME = Path.home()


def set_file_permissions():
    try:
        chmod(HOME / 'www/python/src/citer.log', 0o660)
    except FileNotFoundError:
        close(
            os_open(
                HOME / 'www/python/src/citer.log',
                O_CREAT | O_EXCL | O_WRONLY,
                0o660,
            )
        )
    chmod(HOME / 'www/python/src/config.py', 0o660)


def write_uwsgi_ini():
    (HOME / 'www/python/uwsgi.ini').write_bytes(
        b'[uwsgi]\nenable-threads = true\n'
    )


def write_webservice_template():
    # https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web#Webservice_templates
    (HOME / 'service.template').write_bytes(b'cpu: 3\nmem: 2Gi\n')


def copy_config():
    committer_date = (
        check_output(
            [
                'git',
                '-C',
                f'{HOME}/www/python/src',
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
        return os_open(path, flags, 0o660)

    with open(
        HOME / 'www/python/src/config.py', 'wb', opener=opener
    ) as src_config:
        src_config.write(
            sub(
                b"(USER_AGENT = '.*)'\n",
                rb'\1 v' + committer_date + b"'\n",
                (HOME / '.citer_config').read_bytes(),
                1,
            )
        )


def main():
    copy_config()
    write_uwsgi_ini()
    write_webservice_template()
    set_file_permissions()


if __name__ == '__main__':
    main()
