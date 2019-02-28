#!/usr/bin/env python3
"""Update the tool on toolforge."""

from pathlib import Path
from shutil import copyfile
from subprocess import run

HOME = Path.home()
TOOL_NAME = HOME.name
if TOOL_NAME == 'yadfa':
    LANG = 'fa'
else:
    LANG = 'en'
SRC = HOME / 'www/python/src'


def clone_repo():
    if not SRC.exists():
        run(f'git clone --depth 1 https://github.com/5j9/citer.git {SRC}',
            shell=True, check=True)
    else:
        run(f'git fetch -C {SRC} --all --depth 1', shell=True, check=True)
        run(f'git reset -C {SRC} --hard origin/master', shell=True, check=True)


def latest_ve_path():
    return sorted((HOME / 'pythons').glob('ve*'))[-1] / 'bin/python'


# def fix_shebang():
#     app_py_path = SRC / "app.py"
#     with open(app_py_path, encoding='utf8') as f:
#         app_py = f.read()
#     new_app_py = app_py.replace('/usr/bin/python', str(latest_ve_path()))
#     with open(app_py_path, 'w', encoding='utf8') as f:
#         f.write(new_app_py)


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
    copyfile(str(HOME / '.config.py'), 'config.py')
    try:
        Path(HOME / 'error.log').unlink()
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    clone_repo()
    set_file_permissions()
    configure()
    run(f'pip install -rU {SRC / "requirements.txt"}', shell=True, check=True)
    try:  # To prevent corrupt manifest file. See T164245.
        Path(HOME / 'service.manifest').unlink()
    except FileNotFoundError:
        pass
    run('webservice --backend=kubernetes python restart',
        shell=True, check=True)
    print('All Done!')
