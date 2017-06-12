#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template
from os import name as osname
from zlib import adler32

from src.commons import Response


# Predefined responses
DEFAULT_RESPONSE = Response(
    sfn='Generated citation will appear here...', cite='', ref='', error='0'
)

UNDEFINED_INPUT_RESPONSE = Response(
    sfn='Undefined input.',
    cite='Sorry, the input was not recognized. The error was logged.',
    ref='',
    error='100',
)

HTTPERROR_RESPONSE = Response(
    sfn='HTTP error:',
    cite='One or more of the web resources required to '
    'create this citation are not accessible at this moment.',
    ref='',
    error='100',
)

OTHER_EXCEPTION_RESPONSE = Response(
    sfn='An unknown error occurred.',
    cite='The error was logged.',
    ref='',
    error='100',
)

CSS = open('src/html/en.css', 'rb').read()
# Invalidate cache after css change.
CSS = CSS.replace(
    b'"stylesheet" href="static/en',
    b'"stylesheet" href="static/en' + str(adler32(CSS)).encode(),
)
CSS_HEADERS = [
    ('Content-Type', 'text/css; charset=UTF-8'),
    ('Content-Length', str(len(CSS))),
    ('Cache-Control', 'max-age=31536000'),
]

JS = open('src/html/en.js', 'rb').read()
# Invalidate cache after css change.
JS_HEADERS = [
    ('Content-Type', 'application/javascript; charset=UTF-8'),
    ('Content-Length', str(len(JS))),
    ('Cache-Control', 'max-age=31536000'),
]

# None-zero-padded day directive is os dependant ('%#d' or '%-d')
# See http://stackoverflow.com/questions/904928/
HTML_TEMPLATE = Template(
    open('src/html/en.html', encoding='utf8').read().replace(
        # Invalidate css cache after any change in css file.
        '"stylesheet" href="static/en',
        '"stylesheet" href="static/en' + str(adler32(CSS)),
    ).replace(
        # Invalidate js cache after any change in js file.
        'src="/static/en',
        'src="/static/en' + str(adler32(JS)),
    )
    .replace('$d', '%#d' if osname == 'nt' else '%-d')
)


def response_to_html(response):
    """Insert the response into the HTML_TEMPLATE and return response_body."""
    return HTML_TEMPLATE.safe_substitute(
        # **response._asdict(), did not work on yadkard but worked on yadfa!
        sfn=response.sfn,
        cite=response.cite,
        ref=response.ref,
        error=response.error,
    )