"""HTML skeleton of predefined en responses."""


from string import Template
from os import name as osname
from os.path import dirname
from zlib import adler32
from config import STATIC_PATH


htmldir = dirname(__file__)

# Predefined responses
DEFAULT_SCR = (
    'Generated citation will appear here...', '', '')

UNDEFINED_INPUT_SCR = (
    'Undefined input.',
    'Sorry, the input was not recognized.',
    '')

HTTPERROR_SCR = (
    'HTTP error:',
    'One or more of the web resources required to '
    'create this citation are not accessible at this moment.',
    '')

OTHER_EXCEPTION_SCR = (
    'An unknown error occurred.',
    '',
    '')

CSS = open(htmldir + '/en.css', 'rb').read()
CSS_HEADERS = [
    ('Content-Type', 'text/css; charset=UTF-8'),
    ('Content-Length', str(len(CSS))),
    ('Cache-Control', 'immutable, public, max-age=31536000')]

JS = open(htmldir + '/en.js', 'rb').read()
# Invalidate cache after css change.
JS_HEADERS = [
    ('Content-Type', 'application/javascript; charset=UTF-8'),
    ('Content-Length', str(len(JS))),
    ('Cache-Control', 'immutable, public, max-age=31536000')]

# None-zero-padded day directive is os dependant ('%#d' or '%-d')
# See http://stackoverflow.com/questions/904928/
HTML_SUBST = Template(
    open(htmldir + '/en.html', encoding='utf8').read().replace(
        # Invalidate css cache after any change in css file.
        '"stylesheet" href="./static/en',
        '"stylesheet" href="' + STATIC_PATH + str(adler32(CSS)),
        1,
    ).replace(
        # Invalidate js cache after any change in js file.
        'src="./static/en',
        'src="' + STATIC_PATH + str(adler32(JS)),
        1,
    ).replace('{d}', '#d' if osname == 'nt' else '-d')
).substitute


def scr_to_html(sfn_cit_ref: tuple, date_format: str, input_type: str):
    """Insert sfn_cit_ref into the HTML template and return response_body."""
    date_format = date_format or '%Y-%m-%d'
    sfn, cit, ref = sfn_cit_ref
    return HTML_SUBST(
        sfn=sfn, cit=cit, ref=ref,
    ).replace(date_format + '"', date_format + '" checked', 1).replace(
        '="' + input_type + '"', '="' + input_type + '" selected', 1)
