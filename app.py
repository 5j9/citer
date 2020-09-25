from collections import defaultdict
from html import unescape
from logging import getLogger, Formatter, WARNING, INFO
from logging.handlers import RotatingFileHandler
from os.path import dirname
from urllib.parse import parse_qs, urlparse, unquote
from wsgiref.headers import Headers

from requests import ConnectionError as RequestsConnectionError

from config import LANG
from lib.ketabir import ketabir_scr
from lib.commons import uninum2en, scr_to_json
from lib.doi import doi_scr, DOI_SEARCH
from lib.googlebooks import googlebooks_scr
from lib.isbn_oclc import (
    ISBN_10OR13_SEARCH, IsbnError, isbn_scr, oclc_scr)
from lib.noorlib import noorlib_scr
from lib.noormags import noormags_scr
from lib.pubmed import pmcid_scr, pmid_scr
from lib.urls import urls_scr
from lib.waybackmachine import waybackmachine_scr
if LANG == 'en':
    from lib.html.en import (
        DEFAULT_SCR,
        UNDEFINED_INPUT_SCR,
        HTTPERROR_SCR,
        OTHER_EXCEPTION_SCR,
        scr_to_html,
        CSS,
        CSS_HEADERS,
        JS,
        JS_HEADERS)
else:
    from lib.html.fa import (
        DEFAULT_SCR,
        UNDEFINED_INPUT_SCR,
        HTTPERROR_SCR,
        OTHER_EXCEPTION_SCR,
        scr_to_html,
        CSS,
        CSS_HEADERS)


def google_encrypted_scr(url, parsed_url, date_format):
    if parsed_url[2][:7] in {'/books', '/books/'}:
        # sample urls:
        # https://encrypted.google.com/books?id=6upvonUt0O8C
        # https://www.google.com/books?id=bwfoCAAAQBAJ&pg=PA32
        # https://www.google.com/books/edition/_/bwfoCAAAQBAJ?gbpv=1&pg=PA32
        return googlebooks_scr(parsed_url, date_format)
    return urls_scr(url, date_format)


TLDLESS_NETLOC_RESOLVER = {
    'ketab': ketabir_scr,

    'noorlib': noorlib_scr,
    'noormags': noormags_scr,

    'web.archive': waybackmachine_scr,
    'web-beta.archive': waybackmachine_scr,

    'books.google.co': googlebooks_scr,
    'books.google.com': googlebooks_scr,
    'books.google': googlebooks_scr,

    'google': google_encrypted_scr,
    'encrypted.google': google_encrypted_scr,
}.get

RESPONSE_HEADERS = Headers([('Content-Type', 'text/html; charset=UTF-8')])


getLogger('requests').setLevel(WARNING)
getLogger('langid').setLevel(WARNING)


def get_root_logger():
    custom_logger = getLogger()
    custom_logger.setLevel(INFO)
    srcdir = dirname(__file__)
    handler = RotatingFileHandler(
        filename=f'{srcdir}/citer.log',
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


def url_doi_isbn_scr(user_input, date_format) -> tuple:
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
        parsed_url = urlparse(url)
        # TLD stands for top-level domain
        tldless_netloc = parsed_url[1].rpartition('.')[0]
        resolver = TLDLESS_NETLOC_RESOLVER(
            tldless_netloc[4:] if tldless_netloc.startswith('www.')
            else tldless_netloc)
        if resolver:
            if resolver is googlebooks_scr:
                return resolver(parsed_url, date_format)
            elif resolver is google_encrypted_scr:
                return resolver(url, parsed_url, date_format)
            return resolver(url, date_format)
        # DOIs contain dots
        m = DOI_SEARCH(unescape(en_user_input))
        if m:
            return doi_scr(m[1], True, date_format)
        return urls_scr(url, date_format)
    else:
        # We can check user inputs containing dots for ISBNs, but probably is
        # error prone.
        m = ISBN_10OR13_SEARCH(en_user_input)
        if m:
            try:
                return isbn_scr(m[0], True, date_format)
            except IsbnError:
                pass
        return UNDEFINED_INPUT_SCR


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
        response_body = scr_to_html(
            DEFAULT_SCR, date_format, input_type
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
            response_body = scr_to_json(HTTPERROR_SCR)
        else:
            response_body = scr_to_html(
                HTTPERROR_SCR, date_format, input_type)
    except Exception:
        status = '500 Internal Server Error'
        LOGGER.exception(user_input)
        if output_format == 'json':
            response_body = scr_to_json(OTHER_EXCEPTION_SCR)
        else:
            response_body = scr_to_html(
                OTHER_EXCEPTION_SCR, date_format, input_type)
    else:
        status = '200 OK'
        if output_format == 'json':
            response_body = scr_to_json(response)
        else:
            response_body = scr_to_html(
                response, date_format, input_type)
    response_body = response_body.encode()
    RESPONSE_HEADERS['Content-Length'] = str(len(response_body))
    start_response(status, RESPONSE_HEADERS.items())
    return [response_body]


input_type_to_resolver = defaultdict(
    lambda: url_doi_isbn_scr, {
        'url-doi-isbn': url_doi_isbn_scr,  # todo: can be removed?
        'pmid': pmid_scr,
        'pmcid': pmcid_scr,
        'oclc': oclc_scr})


if __name__ == '__main__':
    # note that app.py is not run as '__main__' in kubernetes
    try:
        from flup.server.fcgi import WSGIServer
        WSGIServer(app).run()
    except ImportError:  # on local computer
        from wsgiref.simple_server import make_server
        httpd = make_server('localhost', 5000, app)
        httpd.serve_forever()
