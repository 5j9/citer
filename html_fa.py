#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template

from commons import BaseResponse


class Response(BaseResponse):

    """Create the responce object used by the main application."""

    def __init__(self, sfn, cite, error='100'):
        self.sfn = sfn
        self.cite = cite
        self.error = error


def response_to_html(response):
    """Insert the response into the HTML_TEMPLATE and return response_body."""
    return HTML_TEMPLATE.safe_substitute(
        sfn=response.sfn,
        cite=response.cite,
        ref=response.ref,
        error=response.error,
    )


HTML_TEMPLATE = Template(open('html_fa.html', encoding='utf8').read())

# Predefined responses
DEFAULT_RESPONSE = Response(
    'یادکرد ساخته‌شده اینجا نمایان خواهد شد...', '', '??'
)
HTTPERROR_RESPONSE = Response(
    'خطای اچ‌تی‌تی‌پی:',
    'یک یا چند مورد از منابع اینترنتی مورد '
    'نیاز برای ساخت این یادکرد در این لحظه '
    'در دسترس نیستند. (و یا ورودی نامعتبر است)',
)
OTHER_EXCEPTION_RESPONSE = Response(
    'خطای ناشناخته‌ای رخ داد..', 'اطلاعات خطا در سیاهه ثبت شد.'
)
UNDEFINED_INPUT_RESPONSE = Response(
    'Undefined input.',
    'Sorry, the input was not recognized. The error was logged.',
)
