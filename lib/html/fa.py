#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the predefined fa responses."""


from string import Template
from zlib import adler32


CSS = open('src/html/fa.css', 'rb').read()
CSS_HEADERS = [
    ('Content-Type', 'text/css; charset=UTF-8'),
    ('Content-Length', str(len(CSS))),
    ('Cache-Control', 'max-age=31536000'),
]

HTML_SUBST = Template(
    open('src/html/fa.html', encoding='utf8').read().replace(
        # Invalidate css cache after any change in css file.
        '"stylesheet" href="./static/fa',
        '"stylesheet" href="./static/fa' + str(adler32(CSS)),
    )
).substitute

# Predefined responses
DEFAULT_SFN_CIT_REF = ('یادکرد ساخته‌شده اینجا نمایان خواهد شد...', '', '')
HTTPERROR_SFN_CIT_REF = (
    'خطای اچ‌تی‌تی‌پی:',
    'یک یا چند مورد از منابع اینترنتی مورد '
    'نیاز برای ساخت این یادکرد در این لحظه '
    'در دسترس نیستند و یا ورودی نامعتبر است.',
    '',
)
OTHER_EXCEPTION_SFN_CIT_REF = (
    'خطای ناشناخته‌ای رخ داد..',
    'اطلاعات خطا در سیاهه ثبت شد.',
    '',
)
UNDEFINED_INPUT_SFN_CIT_REF = (
    'ورودی تجزیه‌ناپذیر',
    'پوزش، ورودی قابل پردازش نبود. خطا در سیاهه ثبت شد.',
    '',
)


def sfn_cit_ref_to_html(sfn_cit_ref: tuple, date_format: str, input_type: str):
    """Insert sfn_cite_ref into the HTML template and return response_body."""
    sfn, cit, ref = sfn_cit_ref
    return HTML_SUBST(sfn=sfn, cit=cit, ref=ref).replace(
        '="' + input_type + '"', '="' + input_type + '" selected', 1
    )
