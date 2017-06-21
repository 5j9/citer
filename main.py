#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
from urllib.parse import parse_qs, urlparse, unquote
from html import unescape
from wsgiref.headers import Headers

try:
    from flup.server.fcgi import WSGIServer
except ImportError:
    from wsgiref.simple_server import make_server
import requests

from config import lang
from src.noormags import noormags_response
from src.googlebooks import googlebooks_response
from src.noorlib import noorlib_response
from src.adinebook import adinehbook_response
from src.urls import urls_response
from src.doi import doi_response, DOI_SEARCH
from src.commons import uninum2en, response_to_json
from src.isbn import ISBN13_SEARCH, ISBN10_SEARCH, IsbnError, isbn_response
from src.waybackmachine import waybackmachine_response
if lang == 'en':
    from src.html.en import (
        DEFAULT_RESPONSE,
        UNDEFINED_INPUT_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        response_to_html,
        CSS,
        CSS_HEADERS,
        JS,
        JS_HEADERS,
    )
else:
    from src.html.fa import (
        DEFAULT_RESPONSE,
        UNDEFINED_INPUT_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        response_to_html,
        CSS,
        CSS_HEADERS,
    )


NETLOC_TO_RESPONSE = {
    'www.adinehbook.com': adinehbook_response,
    'www.adinebook.com': adinehbook_response,
    'adinebook.com': adinehbook_response,
    'adinehbook.com': adinehbook_response,
    'www.noorlib.ir': noorlib_response,
    'www.noorlib.com': noorlib_response,
    'noorlib.com': noorlib_response,
    'noorlib.ir': noorlib_response,
    'www.noormags.ir': noormags_response,
    'www.noormags.com': noormags_response,
    'noormags.com': noormags_response,
    'web.archive.org': waybackmachine_response,
    'web-beta.archive.org': waybackmachine_response,
}

RESPONSE_HEADERS = Headers([('Content-Type', 'text/html; charset=UTF-8')])


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


def get_response(user_input, date_format):
    if not user_input:
        # on first run user_input is ''
        return DEFAULT_RESPONSE
    en_user_input = unquote(uninum2en(user_input))
    # Checking the user input for dot is important because
    # the use of dotless domains is prohibited.
    # See: https://features.icann.org/dotless-domains
    if '.' in en_user_input:
        # Try predefined URLs
        # Todo: The following code could be done in threads.
        if not user_input.startswith('http'):
            url = 'http://' + user_input
        else:
            url = user_input
        netloc = urlparse(url)[1]
        if '.google.com/books' in url:
            return googlebooks_response(url, date_format)
        response_getter = NETLOC_TO_RESPONSE.get(netloc)
        if response_getter:
            return response_getter(url, date_format)
        # DOIs contain dots
        m = DOI_SEARCH(unescape(en_user_input))
        if m:
            return doi_response(m.group(1), pure=True, date_format=date_format)
        return urls_response(url, date_format)
    else:
        # We can check user inputs containing dots for ISBNs, but probably is
        # error prone.
        m = ISBN13_SEARCH(en_user_input) or ISBN10_SEARCH(en_user_input)
        if m:
            try:
                return isbn_response(m.group(), True, date_format)
            except IsbnError:
                pass
        return UNDEFINED_INPUT_RESPONSE


def application(environ, start_response):
    query_dict_get = parse_qs(environ['QUERY_STRING']).get

    path_info = environ['PATH_INFO']
    if '/static/' in path_info:
        if path_info.endswith('.css'):
            start_response('200 OK', CSS_HEADERS)
            return [CSS]
        else:
            # path_info.endswith('.js') and config.lang == 'en'
            start_response('200 OK', JS_HEADERS)
            return [JS]

    action = query_dict_get('action', [''])[0]  # apiquery
    # Warning: input is not escaped!
    user_input = query_dict_get('user_input', [''])[0].strip()
    date_format = query_dict_get('dateformat', [''])[0].strip()
    # noinspection PyBroadException
    try:
        response = get_response(user_input, date_format)
    except requests.ConnectionError:
        status = '500 ConnectionError'
        logger.exception(user_input)
        if action == 'apiquery':
            response_body = HTTPERROR_RESPONSE.api_json()
        else:
            response_body = response_to_html(HTTPERROR_RESPONSE, date_format)
    except Exception:
        status = '500 Internal Server Error'
        logger.exception(user_input)
        if action == 'apiquery':
            response_body = OTHER_EXCEPTION_RESPONSE.api_json()
        else:
            response_body = response_to_html(
                OTHER_EXCEPTION_RESPONSE, date_format
            )
    else:
        status = '200 OK'
        if action == 'apiquery':
            response_body = response_to_json(response)
        else:
            response_body = response_to_html(response, date_format)
    response_body = response_body.encode()
    RESPONSE_HEADERS['Content-Length'] = str(len(response_body))
    start_response(status, RESPONSE_HEADERS.items())
    return [response_body]


if __name__ == '__main__':
    logger = mylogger()
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("langid").setLevel(logging.WARNING)
    try:
        # on remote server
        WSGIServer(application).run()
    except NameError:
        # on local computer
        httpd = make_server('localhost', 5000, application)
        httpd.serve_forever()
