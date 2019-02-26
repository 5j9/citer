#!/usr/bin/env python3
"""Update the tool on toolforge."""

from os import chdir
from pathlib import Path
from shutil import copyfile
from subprocess import run

HOME = Path.home()
TOOL_NAME = HOME.name
if TOOL_NAME == 'yadfa':
    LANG = 'fa'
else:
    LANG = 'en'
CITER = HOME / 'citer'

LIGHTTPD_CONF = f'''#Main configuration:
fastcgi.server += ( "/{TOOL_NAME}" =>
    ((
        "socket" => "/tmp/{TOOL_NAME}-fcgi.socket",
        "bin-path" => "/data/project/$TOOL/citer/app.py",
        "check-local" => "disable",
        "max-procs" => 1,
    ))
)
url.redirect = ( "^.*/{TOOL_NAME}$" => "https://tools.wmflabs.org/{
TOOL_NAME}/" )'''

CONF_PY = f'''__version__ = '2018.08.23'
LANG = 'en'
USER_AGENT = 'https://tools.wmflabs.org/citer/ v' + __version__

# https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Frequency_Timing_and_Registrati
NCBI_EMAIL = ''
NCBI_TOOL = '5j9.citer@github.com'
# https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
NCBI_API_KEY = '7907f7ca634d6de5808137b8298ed476f408'
'''


def create_lighttpd_conf():
    try:
        with open(HOME / '.lighttpd.conf', 'x') as f:
            f.write(LIGHTTPD_CONF)
    except FileExistsError:
        pass


def clone_repo_and_cd():
    if not CITER.exists():
        run('git clone https://github.com/5j9/citer.git --depth 1',
            shell=True, check=True)
        chdir(CITER)
    else:
        chdir(CITER)
        run('git fetch --all --depth 1', shell=True, check=True)
        run('git reset --hard origin/master', shell=True, check=True)


def latest_ve_path():
    return sorted((HOME / 'pythons').glob('ve*'))[-1] / 'bin/python'


def fix_shebang():
    # If python path is not set correctly then the webservice will fail with:
    # 2017-11-08 18:31:44: (log.c.166) server started
    # 2017-11-08 18:31:44: (mod_fastcgi.c.1103) the fastcgi-backend
    # /data/project/citer/citer/app.py failed to start:
    # 2017-11-08 18:31:44: (mod_fastcgi.c.1107) child exited with status 2
    # /data/project/citer/citer/app.py
    # 2017-11-08 18:31:44: (mod_fastcgi.c.1110) If you're trying to run your
    # app as a FastCGI backend, make sure you're using the FastCGI-enabled
    # version. If this is PHP on Gentoo, add 'fastcgi' to the USE flags.
    # 2017-11-08 18:31:44: (mod_fastcgi.c.1398) [ERROR]: spawning fcgi failed.
    # 2017-11-08 18:31:44: (server.c.1021) Configuration of plugins failed.
    # Going down.
    with open('app.py', encoding='utf8') as f:
        app_py = f.read()
    new_app_py = app_py.replace('/usr/bin/python', str(latest_ve_path()))
    with open('app.py', 'w', encoding='utf8') as f:
        f.write(new_app_py)


def set_file_permissions():
    Path('app.py').chmod(0o771)
    try:
        Path('citer.log').chmod(0o660)
    except FileNotFoundError:
        pass
    Path('config.py').chmod(0o660)


def configure():
    create_lighttpd_conf()
    fix_shebang()
    copyfile(HOME/ '.config.py', 'config.py')
    try:
        Path(HOME / 'error.log').unlink()
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    chdir(HOME)
    clone_repo_and_cd()
    set_file_permissions()
    configure()
    run('pip install -rU requirements.txt', shell=True, check=True)
    try:  # To prevent corrupt manifest file. See T164245.
        Path(HOME / 'service.manifest').unlink()
    except FileNotFoundError:
        pass
    run('webservice restart', shell=True, check=True)
    print('All Done!')
