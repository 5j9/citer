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
from commons import uninum2en
from config import lang
from isbn import ISBN13_SEARCH, ISBN10_SEARCH, IsbnError, IsbnResponse
if lang == 'en':
    from html_en import (
        DEFAULT_RESPONSE,
        UNDEFINED_URL_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        to_html,
    )
else:
    from html_fa import (
        DEFAULT_RESPONSE,
        UNDEFINED_URL_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        to_html,
    )


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


def application(environ, start_response):
    qdict = parse_qs(environ['QUERY_STRING'])
    action = qdict.get('action', [''])[0]  # apiquery
    user_input = qdict.get('user_input', [''])[0]
    # Warning: input is not escaped!
    user_input = user_input.strip()
    date_format = qdict.get('dateformat', [''])[0]
    date_format = date_format.strip()
    if not user_input.startswith('http'):
        url = 'http://' + user_input
    else:
        url = user_input
    netloc = urlparse(url)[1]
    try:
        response = None
        if not user_input:
            # on first run user_input is ''
            response = DEFAULT_RESPONSE
            print(repr(DEFAULT_RESPONSE.ref))
            print(repr(DEFAULT_RESPONSE.sfn))
        elif '.google.com/books' in url:
            response = GoogleBooksResponse(url, date_format)
        elif 'noormags.' in netloc:
            response = NoorMagsResponse(url, date_format)
        elif 'noorlib.ir' in netloc:
            response = NoorLibResponse(url, date_format)
        elif ('adinebook' in netloc) or ('adinehbook' in netloc):
            response = AdineBookResponse(url, date_format)
        if not response:
            # DOI and ISBN check
            en_url = unquote(uninum2en(url))
            try:
                m = DOI_SEARCH(unescape(en_url))
                if m:
                    response = DoiResponse(
                        m.group(1),
                        pure=True,
                        date_format=date_format
                    )
                elif ISBN13_SEARCH(en_url):
                    response = IsbnResponse(
                        ISBN13_SEARCH(en_url).group(0),
                        pure=True,
                        date_format=date_format,
                    )
                elif ISBN10_SEARCH(en_url):
                    response = IsbnResponse(
                        ISBN10_SEARCH(en_url).group(0),
                        pure=True,
                        date_format=date_format,
                    )
            except IsbnError:
                pass
        if not response:
            response = UrlsResponse(url, date_format)
        if not response:
            # All the above cases have been unsuccessful
            response = UNDEFINED_URL_RESPONSE
            logger.info('There was an UNDEFINED_URL_RESPONSE\n' + url)
        if action == 'apiquery':
            response_body = response.api_json()
        else:
            response_body = to_html(response)
    except requests.ConnectionError:
        logger.exception(url)
        if action == 'apiquery':
            response_body = HTTPERROR_RESPONSE.api_json()
        else:
            response_body = to_html(HTTPERROR_RESPONSE)
    except Exception:
        logger.exception(url)
        if action == 'apiquery':
            response_body = OTHER_EXCEPTION_RESPONSE.api_json()
        else:
            response_body = to_html(OTHER_EXCEPTION_RESPONSE)
    status = '200 OK'

    response_headers = [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ('Content-Length', ''),
    ]
    start_response(status, response_headers)

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
