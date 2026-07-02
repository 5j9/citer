from html import escape
from os import name as osname
from os.path import dirname
from string import Template
from zlib import adler32

from config import LANG, STATIC_PATH

htmldir = dirname(__file__)

css = open(f'{htmldir}/common.css', 'rb').read()
if LANG == 'fa':
    css = css.replace(b'right;', b'left;')

ALLOW_ALL_ORIGINS = ('Access-Control-Allow-Origin', '*')
CACHE_FOREVER = ('Cache-Control', 'immutable, public, max-age=31536000')
CSS_HEADERS = (
    ALLOW_ALL_ORIGINS,
    ('Content-Type', 'text/css; charset=UTF-8'),
    ('Content-Length', str(len(css))),
    CACHE_FOREVER,
)

js = open(f'{htmldir}/common.js', 'rb').read()
if LANG == 'en':
    js += open(f'{htmldir}/{LANG}.js', 'rb').read()
# Invalidate cache after css change.
JS_HEADERS = (
    ALLOW_ALL_ORIGINS,
    ('Content-Type', 'application/javascript; charset=UTF-8'),
    ('Content-Length', str(len(js))),
    CACHE_FOREVER,
)

JS_PATH = STATIC_PATH + str(adler32(js))
CSS_PATH = STATIC_PATH + str(adler32(css))
# None-zero-padded day directive is os dependant ('%#d' or '%-d')
# See http://stackoverflow.com/questions/904928/
HTML_SUBST = Template(
    open(f'{htmldir}/{LANG}.html', encoding='utf8')
    .read()
    .replace(
        # Invalidate css cache after any change in css file.
        f'"stylesheet" href="static/{LANG}',
        '"stylesheet" href="' + CSS_PATH,
        1,
    )
    .replace(
        # Invalidate js cache after any change in js file.
        f'src="static/{LANG}',
        'src="' + JS_PATH,
        1,
    )
    .replace('{d}', '#d' if osname == 'nt' else '-d')
).substitute


def scr_to_html(
    scr: tuple, date_format: str, pipe_format: str, input_type: str
):
    """Insert sfn_cit_ref into the HTML template and return response_body."""
    sfn, cit, ref = [escape(i) for i in scr]
    return (
        HTML_SUBST(shortened=sfn + '\n\n' + cit, named_ref=ref)
        .replace(f'{date_format}"', f'{date_format}" checked', 1)
        .replace(f'{pipe_format}"', f'{pipe_format}" checked', 1)
        .replace(f'="{input_type}"', f'="{input_type}" selected', 1)
    )


# Predefined responses
if LANG == 'en':
    default_scr = ('Generated citation will appear here...', '', '')

    httperror_scr = (
        'HTTP error:',
        'One or more of the web resources required to '
        'create this citation are not accessible at this moment.',
        '',
    )

else:  # LANG == 'fa'
    # Predefined responses
    default_scr = ('یادکرد ساخته‌شده اینجا نمایان خواهد شد...', '', '')
    httperror_scr = (
        'خطای اچ‌تی‌تی‌پی:',
        'یک یا چند مورد از منابع اینترنتی مورد '
        'نیاز برای ساخت این یادکرد در این لحظه '
        'در دسترس نیستند و یا ورودی نامعتبر است.',
        '',
    )
