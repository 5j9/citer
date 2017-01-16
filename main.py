#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import urllib.parse

try:
    from flup.server.fcgi import WSGIServer
except ImportError:
    from wsgiref.simple_server import make_server
import requests

import noormags
import googlebooks
import noorlib
import adinebook
import urls
import doi
import isbn
import commons
import config
if config.lang == 'en':
    import html_en as html
    from html_en import (
        DEFAULT_RESPONSE,
        UNDEFINED_URL_RESPONSE,
        HTTPERROR_RESPONSE,
        OTHER_EXCEPTION_RESPONSE,
        to_html,
    )
else:
    import html_fa as html
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
    qdict = urllib.parse.parse_qs(environ['QUERY_STRING'])
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
    netloc = urllib.parse.urlparse(url)[1]
    try:
        response = None
        if not user_input:
            # on first run user_input is ''
            response = DEFAULT_RESPONSE
            print(repr(DEFAULT_RESPONSE.ref))
            print(repr(DEFAULT_RESPONSE.sfn))
        elif '.google.com/books' in url:
            response = googlebooks.Response(url, date_format)
        elif 'noormags.' in netloc:
            response = noormags.Response(url, date_format)
        elif 'noorlib.ir' in netloc:
            response = noorlib.Response(url, date_format)
        elif ('adinebook' in netloc) or ('adinehbook' in netloc):
            response = adinebook.Response(url, date_format)
        if not response:
            # DOI and ISBN check
            en_url = urllib.parse.unquote(commons.uninum2en(url))
            try:
                m = doi.DOI_REGEX.search(doi.html.unescape(en_url))
                if m:
                    response = doi.Response(
                        m.group(1),
                        pure=True,
                        date_format=date_format
                    )
                elif isbn.ISBN13_REGEX.search(en_url):
                    response = isbn.Response(
                        isbn.ISBN13_REGEX.search(en_url).group(0),
                        pure=True,
                        date_format=date_format,
                    )
                elif isbn.ISBN10_REGEX.search(en_url):
                    response = isbn.Response(
                        isbn.ISBN10_REGEX.search(en_url).group(0),
                        pure=True,
                        date_format=date_format,
                    )
            except isbn.IsbnError:
                pass
        if not response:
            response = urls.Response(url, date_format)
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
