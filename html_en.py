#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template
from datetime import date

from commons import Response


def response_to_html(response):
    """Insert the response into the HTML_TEMPLATE and return response_body."""
    return HTML_TEMPLATE % (
        response.sfn,
        response.cite,
        response.ref,
        response.error,
    )


HTML_TEMPLATE = Template(open('html_en.html', encoding='utf8').read())

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

TODAY = date.today()
HTML_TEMPLATE = HTML_TEMPLATE.safe_substitute({
    'Ymd': TODAY.strftime('%Y-%m-%d'),
    'BdY': TODAY.strftime('%B %d, %Y'),
    'bdY': TODAY.strftime('%b %d, %Y'),
    'dBY': TODAY.strftime('%d %B %Y'),
    'dbY': TODAY.strftime('%d %b %Y'),
}).replace('%', '%%').replace('$s', '%s')
