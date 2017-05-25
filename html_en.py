#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template
from datetime import date
from os import name as osname

from commons import Response


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

# None-zero-padded day directive is os dependant ('%#d' or '%-d')
# See http://stackoverflow.com/questions/904928/
HTML_TEMPLATE = Template(
    open('html_en.html', encoding='utf8').read()
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