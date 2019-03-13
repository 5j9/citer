#! /usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict
from html import unescape
from logging import getLogger, Formatter, WARNING, INFO
from logging.handlers import RotatingFileHandler
from urllib.parse import parse_qs, urlparse, unquote
from wsgiref.headers import Headers

from requests import ConnectionError as RequestsConnectionError

from config import LANG
from lib.adinebook import adinehbook_sfn_cit_ref
from lib.commons import uninum2en, sfn_cit_ref_to_json
from lib.doi import doi_sfn_cit_ref, DOI_SEARCH
from lib.googlebooks import googlebooks_sfn_cit_ref
from lib.isbn_oclc import (
    ISBN_10OR13_SEARCH, IsbnError, isbn_sfn_cit_ref, oclc_sfn_cit_ref)
from lib.noorlib import noorlib_sfn_cit_ref
from lib.noormags import noormags_sfn_cit_ref
from lib.pubmed import pmcid_sfn_cit_ref, pmid_sfn_cit_ref
from lib.urls import urls_sfn_cit_ref
from lib.waybackmachine import waybackmachine_sfn_cit_ref
if LANG == 'en':
    from lib.html.en import (
        DEFAULT_SFN_CIT_REF,
        UNDEFINED_INPUT_SFN_CIT_REF,
        HTTPERROR_SFN_CIT_REF,
        OTHER_EXCEPTION_SFN_CIT_REF,
        sfn_cit_ref_to_html,
        CSS,
        CSS_HEADERS,
        JS,
        JS_HEADERS)
else:
    from lib.html.fa import (
        DEFAULT_SFN_CIT_REF,
        UNDEFINED_INPUT_SFN_CIT_REF,
        HTTPERROR_SFN_CIT_REF,
        OTHER_EXCEPTION_SFN_CIT_REF,
        sfn_cit_ref_to_html,
        CSS,
        CSS_HEADERS)


TLDLESS_NETLOC_RESOLVER = {
    'adinebook': adinehbook_sfn_cit_ref,
    'adinehbook': adinehbook_sfn_cit_ref,
    'noorlib': noorlib_sfn_cit_ref,
    'noormags': noormags_sfn_cit_ref,
    'web.archive': waybackmachine_sfn_cit_ref,
    'web-beta.archive': waybackmachine_sfn_cit_ref,
    'books.google.co': googlebooks_sfn_cit_ref,
    'books.google': googlebooks_sfn_cit_ref,
}.get

RESPONSE_HEADERS = Headers([('Content-Type', 'text/html; charset=UTF-8')])


getLogger('requests').setLevel(WARNING)
getLogger('langid').setLevel(WARNING)


def get_root_logger():
    custom_logger = getLogger()
    custom_logger.setLevel(INFO)
    handler = RotatingFileHandler(
        filename='citer.log',
        mode='a',
        maxBytes=20000,
        backupCount=0,
        encoding='utf-8',
        delay=0)
    handler.setLevel(INFO)
    handler.setFormatter(
        Formatter('\n%(asctime)s\n%(levelname)s\n%(message)s\n'))
    custom_logger.addHandler(handler)
    return custom_logger


LOGGER = get_root_logger()


def url_doi_isbn_to_sfn_cit_ref(user_input, date_format) -> tuple:
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
        # TLD stands for top-level domain
        tldless_netloc = urlparse(url)[1].rpartition('.')[0]
        resolver = TLDLESS_NETLOC_RESOLVER(
            tldless_netloc[4:] if tldless_netloc.startswith('www.')
            else tldless_netloc)
        if resolver:
            return resolver(url, date_format)
        # DOIs contain dots
        m = DOI_SEARCH(unescape(en_user_input))
        if m:
            return doi_sfn_cit_ref(m.group(1), True, date_format)
        return urls_sfn_cit_ref(url, date_format)
    else:
        # We can check user inputs containing dots for ISBNs, but probably is
        # error prone.
        m = ISBN_10OR13_SEARCH(en_user_input)
        if m:
            try:
                return isbn_sfn_cit_ref(m.group(), True, date_format)
            except IsbnError:
                pass
        return UNDEFINED_INPUT_SFN_CIT_REF


def app(environ, start_response):
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

    date_format = query_dict_get('dateformat', [''])[0].strip()

    input_type = query_dict_get('input_type', [''])[0]

    # Warning: input is not escaped!
    user_input = query_dict_get('user_input', [''])[0].strip()
    if not user_input:
        response_body = sfn_cit_ref_to_html(
            DEFAULT_SFN_CIT_REF, date_format, input_type
        ).encode()
        RESPONSE_HEADERS['Content-Length'] = str(len(response_body))
        start_response('200 OK', RESPONSE_HEADERS.items())
        return [response_body]

    output_format = query_dict_get('output_format', [''])[0]  # apiquery

    resolver = input_type_to_resolver[input_type]
    # noinspection PyBroadException
    try:
        response = resolver(user_input, date_format)
    except RequestsConnectionError:
        status = '500 ConnectionError'
        LOGGER.exception(user_input)
        if output_format == 'json':
            response_body = sfn_cit_ref_to_json(HTTPERROR_SFN_CIT_REF)
        else:
            response_body = sfn_cit_ref_to_html(
                HTTPERROR_SFN_CIT_REF, date_format, input_type)
    except Exception:
        status = '500 Internal Server Error'
        LOGGER.exception(user_input)
        if output_format == 'json':
            response_body = sfn_cit_ref_to_json(OTHER_EXCEPTION_SFN_CIT_REF)
        else:
            response_body = sfn_cit_ref_to_html(
                OTHER_EXCEPTION_SFN_CIT_REF, date_format, input_type)
    else:
        status = '200 OK'
        if output_format == 'json':
            response_body = sfn_cit_ref_to_json(response)
        else:
            response_body = sfn_cit_ref_to_html(
                response, date_format, input_type)
    response_body = response_body.encode()
    RESPONSE_HEADERS['Content-Length'] = str(len(response_body))
    start_response(status, RESPONSE_HEADERS.items())
    return [response_body]


input_type_to_resolver = defaultdict(
    lambda: url_doi_isbn_to_sfn_cit_ref, {
        'url-doi-isbn': url_doi_isbn_to_sfn_cit_ref,
        'pmid': pmid_sfn_cit_ref,
        'pmcid': pmcid_sfn_cit_ref,
        'oclc': oclc_sfn_cit_ref})


if __name__ == '__main__':
    # note that app.py is not run as '__main__' in kubernetes
    try:
        from flup.server.fcgi import WSGIServer
        WSGIServer(app).run()
    except ImportError:  # on local computer
        from wsgiref.simple_server import make_server
        httpd = make_server('localhost', 5000, app)
        httpd.serve_forever()
