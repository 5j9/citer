from os.path import dirname
from string import Template
from zlib import adler32

from config import STATIC_PATH

htmldir = dirname(__file__)

CSS = open(htmldir + '/fa.css', 'rb').read()
CSS_HEADERS = [
    ('Content-Type', 'text/css; charset=UTF-8'),
    ('Content-Length', str(len(CSS))),
    ('Cache-Control', 'max-age=31536000')]

CSS_PATH = STATIC_PATH + str(adler32(CSS))
JS_PATH = 'STATIC_PATH/<does_not_exist>.js'
HTML_SUBST = Template(
    open(htmldir + '/fa.html', encoding='utf8').read().replace(
        # Invalidate css cache after any change in css file.
        '"stylesheet" href="static/fa',
        '"stylesheet" href="' + CSS_PATH,
    )
).substitute

# Predefined responses
DEFAULT_SCR = ('یادکرد ساخته‌شده اینجا نمایان خواهد شد...', '', '')
HTTPERROR_SCR = (
    'خطای اچ‌تی‌تی‌پی:',
    'یک یا چند مورد از منابع اینترنتی مورد '
    'نیاز برای ساخت این یادکرد در این لحظه '
    'در دسترس نیستند و یا ورودی نامعتبر است.',
    '')
OTHER_EXCEPTION_SCR = (
    'خطای ناشناخته‌ای رخ داد..',
    'اطلاعات خطا در سیاهه ثبت شد.',
    '')
UNDEFINED_INPUT_SCR = (
    'ورودی تجزیه‌ناپذیر',
    'پوزش، ورودی قابل پردازش نبود. خطا در سیاهه ثبت شد.',
    '')


def scr_to_html(sfn_cit_ref: tuple, date_format: str, input_type: str):
    """Insert sfn_cite_ref into the HTML template and return response_body."""
    sfn, cit, ref = sfn_cit_ref
    return HTML_SUBST(sfn=sfn, cit=cit, ref=ref).replace(
        '="' + input_type + '"', '="' + input_type + '" selected', 1)
