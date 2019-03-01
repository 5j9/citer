#!/usr/bin/env python3
"""Update the tool on toolforge."""

from pathlib import Path
from os.path import expanduser, exists
from shutil import copyfile
from subprocess import run

HOME = expanduser('~')
TOOL_NAME = Path(HOME).name
if TOOL_NAME == 'yadfa':
    LANG = 'fa'
else:
    LANG = 'en'
SRC = HOME + '/www/python/src'


def clone_repo():
    if not exists(SRC):
        run('git clone --depth 1 https://github.com/5j9/citer.git ' + SRC,
            shell=True, check=True)
    else:
        run('git fetch -C ' + SRC + ' --all --depth 1', shell=True, check=True)
        run('git reset -C ' + SRC + ' --hard origin/master',
            shell=True, check=True)


def set_file_permissions():
    Path('app.py').chmod(0o771)
    try:
        Path('citer.log').chmod(0o660)
    except FileNotFoundError:
        pass
    Path('config.py').chmod(0o660)


def configure():
    # fix_shebang()
    # copyfile does not accept PathLike: https://bugs.python.org/issue30235
    copyfile(HOME + '/.config.py', 'config.py')
    try:
        Path(HOME + '/error.log').unlink()
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    clone_repo()
    set_file_permissions()
    configure()
    run('pip install -rU ' + SRC + '/requirements.txt', shell=True, check=True)
    try:  # To prevent corrupt manifest file. See T164245.
        Path(HOME + '/service.manifest').unlink()
    except FileNotFoundError:
        pass
    run('webservice --backend=kubernetes python restart',
        shell=True, check=True)
    print('All Done!')
