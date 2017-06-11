#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template

from src.commons import Response


HTML_TEMPLATE = Template(open('src/html_fa.html', encoding='utf8').read())

# Predefined responses
DEFAULT_RESPONSE = Response(
    sfn='یادکرد ساخته‌شده اینجا نمایان خواهد شد...',
    cite='',
    ref='',
    error='0',
)
HTTPERROR_RESPONSE = Response(
    sfn='خطای اچ‌تی‌تی‌پی:',
    cite='یک یا چند مورد از منابع اینترنتی مورد '
    'نیاز برای ساخت این یادکرد در این لحظه '
    'در دسترس نیستند و یا ورودی نامعتبر است.',
    ref='',
    error='100'
)
OTHER_EXCEPTION_RESPONSE = Response(
    sfn='خطای ناشناخته‌ای رخ داد..',
    cite='اطلاعات خطا در سیاهه ثبت شد.',
    ref='',
    error='100',
)
UNDEFINED_INPUT_RESPONSE = Response(
    sfn='ورودی تجزیه‌ناپذیر',
    cite='پوزش، ورودی قابل پردازش نبود. خطا در سیاهه ثبت شد.',
    ref='',
    error='100',
)


def response_to_html(response: Response):
    """Insert the response into the HTML_TEMPLATE and return response_body."""
    return HTML_TEMPLATE.safe_substitute(**response._asdict())
