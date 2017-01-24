#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template
from datetime import date

from commons import BaseResponse


class Response(BaseResponse):

    """Create the response object used by the main application."""

    def __init__(self, sfn, cite, error='100'):
        self.sfn = sfn
        self.cite = cite
        self.error = error


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
DEFAULT_RESPONSE = Response('Generated citation will appear here...', '', '0')

UNDEFINED_INPUT_RESPONSE = Response(
    'Undefined input.',
    'Sorry, the input was not recognized. The error was logged.',
)

HTTPERROR_RESPONSE = Response(
    'HTTP error:',
    'One or more of the web resources required to '
    'create this citation are not accessible at this moment.',
)

OTHER_EXCEPTION_RESPONSE = Response(
    'An unknown error occurred.', 'The error was logged.'
)

TODAY = date.today()
HTML_TEMPLATE = HTML_TEMPLATE.safe_substitute({
    'Ymd': TODAY.strftime('%Y-%m-%d'),
    'BdY': TODAY.strftime('%B %d, %Y'),
    'bdY': TODAY.strftime('%b %d, %Y'),
    'dBY': TODAY.strftime('%d %B %Y'),
    'dbY': TODAY.strftime('%d %b %Y'),
}).replace('%', '%%').replace('$s', '%s')
