#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging, logging.handlers
import urllib2
from cgi import escape
from urlparse import parse_qs

from yadkardlib import noormags, googlebooks, noorlib, doi, html

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
    fmt = '%(asctime)s\r\n%(levelname)s\r\n%(message)s\r\n\r\n'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def application(environ, start_response):
    qdict = parse_qs(environ['QUERY_STRING'])
    url = qdict.get('url', [''])[0]
    url = escape(url)
    try:
        if not url:
            #on first run url is not defined yet:
            response_body = html.skeleton %html.default_response
        elif 'dx.doi.org' in url:
            obj = doi.Doi(url)
        elif 'noormags.com' in url:
            obj = noormags.NoorMag(url)
        elif 'noorlib.ir' in url:
            obj = noorlib.NoorLib(url)
        elif 'books.google' in url:
            obj = googlebooks.GoogleBook(url)
        else:
            obj = html.ResposeObj(*html.undefined_url_response)
            logger.info('%s\r\n%s' %('there was an undefined_url_response', url))
        
        response_body = html.skeleton %(obj.ref, obj.cite, obj.error)
        
    except urllib2.HTTPError as e:
        #todo:
        print e
        logger.error('%s, %s' %(e, url))
        response_body = html.skeleton %html.httperror_response
    except Exception as e:
        #todo:
        logger.critical('%s, %s' %(e, url))
        print e
        response_body = html.skeleton %html.other_exception_response
    status = '200 OK'

    response_headers = [('Content-Type', 'text/html; charset=UTF-8'),
                  ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)

    return [response_body]

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
