#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import urllib2
from cgi import escape
import urlparse
import requests

from yadkardlib import noormags, googlebooks, noorlib, adinebook, urls
from yadkardlib import doi, isbn, conv, config

if config.lang == 'en':
    from yadkardlib import html_en as html
else:
    from yadkardlib import html_fa as html


def mylogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
                                    filename='./yadkardlib/yadkard.log',
                                    mode='a',
                                    maxBytes=20000,
                                    backupCount=0,
                                    encoding='utf-8',
                                    delay=0)
    handler.setLevel(logging.DEBUG)
    fmt = '\r\n%(asctime)s\r\n%(levelname)s\r\n%(message)s\r\n'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def application(environ, start_response):
    qdict = urlparse.parse_qs(environ['QUERY_STRING'])
    url = qdict.get('url', [''])[0].decode('utf8')
    url = escape(url).strip()
    date_format = qdict.get('dateformat', [''])[0].decode('utf8')
    date_format = escape(date_format).strip()
    if not url.startswith('http'):
        url = 'http://' + url
    netloc = urlparse.urlparse(url)[1]
    try:
        obj = None
        if url == 'http://':
            #on first run url is ''
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
            en_url = conv.fanum2en(url)
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
            logger.info(u'There was an undefined_url_response\r\n' + url)
        response_body = html.skeleton % (obj.ref,
                                        obj.cite,
                                        obj.error)
    except (urllib2.HTTPError, requests.ConnectionError):
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

    return [response_body.encode('utf-8')]

logger = mylogger()

try:
    from flup.server.fcgi import WSGIServer
    #on toolserver:
    WSGIServer(application).run()
except ImportError:
    #on local computer:
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    httpd.serve_forever()
