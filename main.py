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
else:
    import html_fa as html


def mylogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        filename='yadkard.log',
        mode='a',
        maxBytes=20000,
        backupCount=0,
        encoding='utf-8',
        delay=0)
    handler.setLevel(logging.INFO)
    fmt = '\n%(asctime)s\n%(levelname)s\n%(message)s\n'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def application(environ, start_response):
    qdict = urllib.parse.parse_qs(environ['QUERY_STRING'])
    action = qdict.get('action', [''])[0] # apiquery
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
            response = html.default_response
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
                m = doi.re.search(doi.doi_regex, doi.html.unescape(en_url))
                if m:
                    response = doi.Response(m.group(1),
                                       pure=True,
                                       date_format=date_format)
                elif isbn.re.search(isbn.isbn13_regex, en_url):
                    response = isbn.Response(
                        isbn.re.search(isbn.isbn13_regex, en_url).group(0),
                        pure=True,
                        date_format=date_format,)
                elif isbn.re.search(isbn.isbn10_regex, en_url):
                    response = isbn.Response(
                        isbn.re.search(isbn.isbn10_regex, en_url).group(0),
                        pure=True,
                        date_format=date_format,)
            except isbn.IsbnError:
                pass
        if not response:
            response = urls.Response(url, date_format)
        if not response:
            # All the above cases have been unsuccessful
            response = html.undefined_url_response
            logger.info('There was an undefined_url_response\n' + url)
        if action == 'apiquery':
            response_body = response.api_json()
        else:
            response_body = html.response_to_template(response) 
    except (requests.ConnectionError):
        logger.exception(url)
        if action == 'apiquery':
            response_body = html.httperror_response.api_json()
        else:
            response_body = html.response_to_template(html.httperror_response)
    except Exception as e:
        logger.exception(url)
        if action == 'apiquery':
            response_body = html.other_exception_response.api_json()
        else:
            response_body = html.response_to_template(
                html.other_exception_response)
    status = '200 OK'

    response_headers = [('Content-Type', 'text/html; charset=UTF-8'),
                        ('Content-Length', '')
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
    httpd = make_server('localhost', 8051, application)
    httpd.serve_forever()
