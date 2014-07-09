#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import urllib.parse
from cgi import escape

try:
    from flup.server.fcgi import WSGIServer
except ImportError:
    from wsgiref.simple_server import make_server
import requests

import noormags, googlebooks, noorlib, adinebook, urls
import doi, isbn, commons, config
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
    user_input = qdict.get('user_input', [''])[0]
    #cgi.escape() was causing unexpected behaviour
    user_input = user_input.strip()
    date_format = qdict.get('dateformat', [''])[0]
    date_format = escape(date_format).strip()
    if not user_input.startswith('http'):
        url = 'http://' + user_input
    else:
        url = user_input
    netloc = urllib.parse.urlparse(url)[1]
    try:
        obj = None
        if not user_input:
            #on first run user_input is ''
            obj = html.ResposeObj(*html.default_response)
        elif '.google.com/books' in url:
            obj = googlebooks.Citation(url, date_format)
        elif 'noormags.' in netloc:
            obj = noormags.Citation(url, date_format)
        elif 'noorlib.ir' in netloc:
            obj = noorlib.Citation(url, date_format)
        elif ('adinebook' in netloc) or ('adinehbook' in netloc):
            obj = adinebook.Citation(url, date_format)
        if not obj:
            #DOI and ISBN check
            en_url = commons.fanum2en(url)
            try:
                m = doi.re.search(doi.doi_regex, doi.sax.unescape(en_url))
                if m:
                    obj = doi.Citation(m.group(1),
                                       pure=True,
                                       date_format=date_format)
                elif isbn.re.search(isbn.isbn13_regex, en_url):
                    obj = isbn.Citation(
                        isbn.re.search(isbn.isbn13_regex, en_url).group(0),
                        pure=True,
                        date_format=date_format,)
                elif isbn.re.search(isbn.isbn10_regex, en_url):
                    obj = isbn.Citation(
                        isbn.re.search(isbn.isbn10_regex, en_url).group(0),
                        pure=True,
                        date_format=date_format,)
            except isbn.IsbnError:
                pass
        if not obj:
            obj = urls.Citation(url, date_format)
        if not obj:
            #All the above cases have been unsuccessful
            obj = html.ResposeObj(*html.undefined_url_response)
            logger.info('There was an undefined_url_response\n' + url)
        response_body = html.skeleton % (obj.ref,
                                        obj.cite,
                                        obj.error)
    except (requests.ConnectionError):
        logger.exception(url)
        response_body = html.skeleton % html.httperror_response
    except Exception:
        logger.exception(url)
        response_body = html.skeleton % html.other_exception_response
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
