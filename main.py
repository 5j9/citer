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

from noormags import noormags_response
from googlebooks import googlebooks_response
from noorlib import noorlib_response
from adinebook import adinehbook_response
from urls import urls_response
from doi import doi_response, DOI_SEARCH
from commons import uninum2en, response_to_json
from config import lang
from isbn import ISBN13_SEARCH, ISBN10_SEARCH, IsbnError, isbn_response
from waybackmachine import waybackmachine_response
if lang == 'en':
    from html_en import (
        DEFAULT_RESPONSE,
        UNDEFINED_INPUT_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        response_to_html,
    )
else:
    from html_fa import (
        DEFAULT_RESPONSE,
        UNDEFINED_INPUT_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        response_to_html,
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


def get_response(user_input, date_format):
    if not user_input:
        # on first run user_input is ''
        return DEFAULT_RESPONSE
    en_user_input = unquote(uninum2en(user_input))
    # Checking the user input for dot is important because
    # the use of dotless domains is prohibited.
    # See: https://features.icann.org/dotless-domains
    user_input_contains_dot = '.' in en_user_input
    if user_input_contains_dot:
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
    action = query_dict_get('action', [''])[0]  # apiquery
    # Warning: input is not escaped!
    user_input = query_dict_get('user_input', [''])[0].strip()
    date_format = query_dict_get('dateformat', [''])[0].strip()
    try:
        response = get_response(user_input, date_format)
    except requests.ConnectionError:
        logger.exception(user_input)
        if action == 'apiquery':
            response_body = HTTPERROR_RESPONSE.api_json()
        else:
            response_body = response_to_html(HTTPERROR_RESPONSE)
    except Exception:
        logger.exception(user_input)
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
