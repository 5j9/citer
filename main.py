#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
from urllib.parse import parse_qs, urlparse, unquote
from html import unescape

try:
    from flup.server.fcgi import WSGIServer
except ImportError:
    from wsgiref.simple_server import make_server
import requests

from noormags import NoorMagsResponse
from googlebooks import GoogleBooksResponse
from noorlib import NoorLibResponse
from adinebook import AdineBookResponse
from urls import UrlsResponse
from doi import DoiResponse, DOI_SEARCH
from commons import uninum2en, response_to_json
from config import lang
from isbn import ISBN13_SEARCH, ISBN10_SEARCH, IsbnError, IsbnResponse
if lang == 'en':
    from html_en import (
        DEFAULT_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        response_to_html,
    )
else:
    from html_fa import (
        DEFAULT_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        response_to_html,
    )


NETLOC_TO_RESPONSE = {
    'www.adinehbook.com': AdineBookResponse,
    'www.adinebook.com': AdineBookResponse,
    'adinebook.com': AdineBookResponse,
    'adinehbook.com': AdineBookResponse,
    'www.noorlib.ir': NoorLibResponse,
    'www.noorlib.com': NoorLibResponse,
    'noorlib.com': NoorLibResponse,
    'noorlib.ir': NoorLibResponse,
    'www.noormags.ir': NoorMagsResponse,
    'www.noormags.com': NoorMagsResponse,
    'noormags.com': NoorMagsResponse,
}

RESPONSE_HEADERS = [
    ('Content-Type', 'text/html; charset=UTF-8'),
    ('Content-Length', ''),
]


def mylogger():
    custom_logger = logging.getLogger()
    custom_logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        filename='yadkard.log',
        mode='a',
        maxBytes=20000,
        backupCount=0,
        encoding='utf-8',
        delay=0
    )
    handler.setLevel(logging.INFO)
    fmt = '\n%(asctime)s\n%(levelname)s\n%(message)s\n'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    custom_logger.addHandler(handler)
    return custom_logger


def get_response(user_input, url, netloc, date_format):
    if not user_input:
        # on first run user_input is ''
        return DEFAULT_RESPONSE
    if '.google.com/books' in url:
        return GoogleBooksResponse(url, date_format)
    response_class = NETLOC_TO_RESPONSE.get(netloc)
    if response_class:
        return response_class(url, date_format)
    # DOI and ISBN check
    en_url = unquote(uninum2en(url))
    m = DOI_SEARCH(unescape(en_url))
    if m:
        return DoiResponse(
            m.group(1),
            pure=True,
            date_format=date_format
        )
    m = ISBN13_SEARCH(en_url) or ISBN10_SEARCH(en_url)
    if m:
        try:
            return IsbnResponse(m.group(0), pure=True, date_format=date_format)
        except IsbnError:
            pass
    return UrlsResponse(url, date_format)


def application(environ, start_response):
    qdict = parse_qs(environ['QUERY_STRING'])
    action = qdict.get('action', [''])[0]  # apiquery
    # Warning: input is not escaped!
    user_input = qdict.get('user_input', [''])[0].strip()
    date_format = qdict.get('dateformat', [''])[0].strip()
    if not user_input.startswith('http'):
        url = 'http://' + user_input
    else:
        url = user_input
    netloc = urlparse(url)[1]
    try:
        response = get_response(user_input, url, netloc, date_format)
    except requests.ConnectionError:
        logger.exception(url)
        if action == 'apiquery':
            response_body = HTTPERROR_RESPONSE.api_json()
        else:
            response_body = response_to_html(HTTPERROR_RESPONSE)
    except Exception:
        logger.exception(url)
        if action == 'apiquery':
            response_body = OTHER_EXCEPTION_RESPONSE.api_json()
        else:
            response_body = response_to_html(OTHER_EXCEPTION_RESPONSE)
    else:
        if action == 'apiquery':
            response_body = response_to_json(response)
        else:
            response_body = response_to_html(response)

    start_response('200 OK', RESPONSE_HEADERS)

    return [response_body.encode()]

logger = mylogger()
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("langid").setLevel(logging.WARNING)

try:
    # on remote server
    WSGIServer(application).run()
except NameError:
    # on local computer:
    httpd = make_server('localhost', 5000, application)
    httpd.serve_forever()
