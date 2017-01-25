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

# None-zero-padded day directive is os dependant.
# See http://stackoverflow.com/questions/904928/
NZDD = '%#d' if osname == 'nt' else '%-d'

HTML_TEMPLATE = Template(open('html_en.html', encoding='utf8').read())

BdY_FORMAT = '%B ' + NZDD + ', %Y'
bdY_FORMAT = '%b ' + NZDD + ', %Y'
dBY_FORMAT = NZDD + ' %B %Y'
dbY_FORMAT = NZDD + ' %b %Y'

TODAY = date.today


def response_to_html(response):
    """Insert the response into the HTML_TEMPLATE and return response_body."""
    return HTML_TEMPLATE.safe_substitute(
        d=NZDD,
        Ymd=TODAY().strftime('%Y-%m-%d'),
        BdY=TODAY().strftime(BdY_FORMAT),
        bdY=TODAY().strftime(bdY_FORMAT),
        dBY=TODAY().strftime(dBY_FORMAT),
        dbY=TODAY().strftime(dbY_FORMAT),
        **response._asdict(),
    )