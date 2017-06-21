#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template
from os import name as osname
from zlib import adler32

from src.commons import Response


# Predefined responses
DEFAULT_RESPONSE = Response(
    sfn='Generated citation will appear here...', cite='', ref='',
)

UNDEFINED_INPUT_RESPONSE = Response(
    sfn='Undefined input.',
    cite='Sorry, the input was not recognized. The error was logged.',
    ref='',
)

HTTPERROR_RESPONSE = Response(
    sfn='HTTP error:',
    cite='One or more of the web resources required to '
    'create this citation are not accessible at this moment.',
    ref='',
)

OTHER_EXCEPTION_RESPONSE = Response(
    sfn='An unknown error occurred.',
    cite='The error was logged.',
    ref='',
)

CSS = open('src/html/en.css', 'rb').read()
CSS_HEADERS = [
    ('Content-Type', 'text/css; charset=UTF-8'),
    ('Content-Length', str(len(CSS))),
    ('Cache-Control', 'immutable, public, max-age=31536000'),
]

JS = open('src/html/en.js', 'rb').read()
# Invalidate cache after css change.
JS_HEADERS = [
    ('Content-Type', 'application/javascript; charset=UTF-8'),
    ('Content-Length', str(len(JS))),
    ('Cache-Control', 'immutable, public, max-age=31536000'),
]

# None-zero-padded day directive is os dependant ('%#d' or '%-d')
# See http://stackoverflow.com/questions/904928/
HTML_SUBST = Template(
    open('src/html/en.html', encoding='utf8').read().replace(
        # Invalidate css cache after any change in css file.
        '"stylesheet" href="./static/en',
        '"stylesheet" href="./static/en' + str(adler32(CSS)),
        1,
    ).replace(
        # Invalidate js cache after any change in js file.
        'src="./static/en',
        'src="./static/en' + str(adler32(JS)),
        1,
    )
    .replace('~d', '%#d' if osname == 'nt' else '%-d')
).substitute


def response_to_html(response: Response, date_format: str):
    """Insert the response into the HTML template and return response_body."""
    date_format = date_format or '%Y-%m-%d'
    return HTML_SUBST(
        **response._asdict(),
    ).replace(date_format + '"', date_format + '" checked', 1)
