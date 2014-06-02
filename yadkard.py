#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging, logging.handlers
import urllib2
from cgi import escape
import urlparse

from yadkardlib import noormags, googlebooks, noorlib, adinebook, nyt, bbc,\
     dailymail, mirror, telegraph
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
    if not url.startswith('http'):
        url = 'http://' + url
    try:
        if url == 'http://':
            #on first run url is ''
            obj = html.ResposeObj(*html.default_response)
        elif '.google.com/books' in url:
            obj = googlebooks.GoogleBook(url)
        elif 'nytimes.com/' in url:
            obj = nyt.NYT(url)
        elif 'bbc.co' in urlparse.urlparse(url)[1]:
            obj = bbc.BBC(url)
        elif 'dailymail.' in urlparse.urlparse(url)[1]:
            obj = dailymail.DM(url)
        elif 'mirror.' in urlparse.urlparse(url)[1]:
            obj = mirror.DM(url)
        elif 'telegraph.' in urlparse.urlparse(url)[1]:
            obj = telegraph.DT(url)
        elif 'noormags.com/' in url:
            obj = noormags.NoorMag(url)
        elif 'noorlib.ir/' in url:
            obj = noorlib.NoorLib(url)
        elif 'adinebook.com/gp/product/' in url:
            obj = adinebook.AdineBook(url)
        else:
            en_url = conv.fanum2en(url)
            doi_m = doi.re.search(doi.doi_regex, doi.sax.unescape(en_url))
            if doi_m:
                obj = doi.Doi(doi_m.group(1), pure=True)
            else:
                isbn13_m = isbn.re.search(isbn.isbn13_regex, en_url)
                if isbn13_m:
                    obj = isbn.Isbn(isbn13_m.group(0), pure=True)
                else:
                    isbn10_m = isbn.re.search(isbn.isbn10_regex, en_url)
                    if isbn10_m:
                        obj = isbn.Isbn(isbn10_m.group(0), pure=True)
                    else:
                        obj = html.ResposeObj(*html.undefined_url_response)
                        logger.info(u'There was an undefined_url_response\r\n' +\
                                    url)
        response_body = html.skeleton %(obj.ref,
                                        obj.cite,
                                        obj.error)
    except urllib2.HTTPError:
        logger.exception(url)
        response_body = html.skeleton %html.httperror_response
    except:
        logger.exception(url)
        response_body = html.skeleton %html.other_exception_response
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
