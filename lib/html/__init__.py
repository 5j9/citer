from html import escape
from os import name as osname
from os.path import dirname
from string import Template
from zlib import adler32

from config import LANG, STATIC_PATH

htmldir = dirname(__file__)

CSS = open(f'{htmldir}/common.css', 'rb').read()
if LANG == 'fa':
    CSS = CSS.replace(b'right;', b'left;')
CSS_HEADERS = [
    ('Content-Type', 'text/css; charset=UTF-8'),
    ('Content-Length', str(len(CSS))),
    ('Cache-Control', 'immutable, public, max-age=31536000'),
]

JS = open(f'{htmldir}/common.js', 'rb').read()
if LANG == 'en':
    JS += open(f'{htmldir}/{LANG}.js', 'rb').read()
# Invalidate cache after css change.
JS_HEADERS = [
    ('Content-Type', 'application/javascript; charset=UTF-8'),
    ('Content-Length', str(len(JS))),
    ('Cache-Control', 'immutable, public, max-age=31536000'),
]

JS_PATH = STATIC_PATH + str(adler32(JS))
CSS_PATH = STATIC_PATH + str(adler32(CSS))
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


def scr_to_html(sfn_cit_ref: tuple, date_format: str, input_type: str):
    """Insert sfn_cit_ref into the HTML template and return response_body."""
    sfn, cit, ref = [escape(i) for i in sfn_cit_ref]
    return (
        HTML_SUBST(
            sfn=sfn,
            cit=cit,
            ref=ref,
        )
        .replace(f'{date_format}"', f'{date_format}" checked', 1)
        .replace(f'="{input_type}"', f'="{input_type}" selected', 1)
    )


# Predefined responses
if LANG == 'en':
    DEFAULT_SCR = ('Generated citation will appear here...', '', '')

    HTTPERROR_SCR = (
        'HTTP error:',
        'One or more of the web resources required to '
        'create this citation are not accessible at this moment.',
        '',
    )

else:  # LANG == 'fa'
    # Predefined responses
    DEFAULT_SCR = ('یادکرد ساخته‌شده اینجا نمایان خواهد شد...', '', '')
    HTTPERROR_SCR = (
        'خطای اچ‌تی‌تی‌پی:',
        'یک یا چند مورد از منابع اینترنتی مورد '
        'نیاز برای ساخت این یادکرد در این لحظه '
        'در دسترس نیستند و یا ورودی نامعتبر است.',
        '',
    )
