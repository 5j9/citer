from collections import defaultdict
from html import unescape
from logging import INFO, WARNING, Formatter, getLogger
from logging.handlers import RotatingFileHandler
from os.path import abspath, dirname
from urllib.parse import parse_qs, unquote, urlparse
from wsgiref.headers import Headers

from requests import ConnectionError as RequestsConnectionError, JSONDecodeError

from config import LANG
from lib.commons import ISBN_10OR13_SEARCH, ReturnError, dict_to_sfn_cit_ref, uninum2en
from lib.doi import DOI_SEARCH, doi_to_dict
from lib.googlebooks import url_to_dict as google_books_dict
from lib.isbn_oclc import IsbnError, isbn_to_dict, oclc_dict, worldcat_url_to_dict
from lib.jstor import url_to_dict as jstor_url_to_dict
from lib.ketabir import url_to_dict as ketabir_url_to_dict
from lib.noorlib import url_to_dict as noorlib_url_to_dict
from lib.noormags import url_to_dict as noormags_url_to_dict
from lib.pubmed import pmcid_dict, pmid_dict
from lib.urls import url_to_dict as urls_url_to_dict
from lib.waybackmachine import url_to_dict as archive_url_to_dict

if LANG == 'en':
    from lib.html.en import (
        CSS,
        CSS_HEADERS,
        DEFAULT_SCR,
        HTTPERROR_SCR,
        JS,
        JS_HEADERS,
        OTHER_EXCEPTION_SCR,
        UNDEFINED_INPUT_SCR,
        scr_to_html,
    )
else:
    from lib.html.fa import (
        CSS,
        CSS_HEADERS,
        DEFAULT_SCR,
        HTTPERROR_SCR,
        OTHER_EXCEPTION_SCR,
        UNDEFINED_INPUT_SCR,
        scr_to_html,
    )


def google_encrypted_dict(url, parsed_url, date_format) -> dict:
    if parsed_url[2][:7] in {'/books', '/books/'}:
        # sample urls:
        # https://encrypted.google.com/books?id=6upvonUt0O8C
        # https://www.google.com/books?id=bwfoCAAAQBAJ&pg=PA32
        # https://www.google.com/books/edition/_/bwfoCAAAQBAJ?gbpv=1&pg=PA32
        return google_books_dict(parsed_url, date_format)
    return urls_url_to_dict(url, date_format)


TLDLESS_NETLOC_RESOLVER = {
    'ketab': ketabir_url_to_dict,
    'worldcat': worldcat_url_to_dict,

    'noorlib': noorlib_url_to_dict,
    'noormags': noormags_url_to_dict,

    'web.archive': archive_url_to_dict,
    'web-beta.archive': archive_url_to_dict,

    'books.google.co': google_books_dict,
    'books.google.com': google_books_dict,
    'books.google': google_books_dict,

    'google': google_encrypted_dict,
    'encrypted.google': google_encrypted_dict,

    'jstor': jstor_url_to_dict,
}.get

RESPONSE_HEADERS = Headers([('Content-Type', 'text/html; charset=UTF-8')])


getLogger('requests').setLevel(WARNING)
getLogger('langid').setLevel(WARNING)


def get_root_logger():
    custom_logger = getLogger()
    custom_logger.setLevel(INFO)
    srcdir = dirname(abspath(__file__))
    handler = RotatingFileHandler(
        filename=f'{srcdir}/citer.log',
        mode='a',
        maxBytes=20000,
        backupCount=0,
        encoding='utf-8',
    )
    handler.setLevel(INFO)
    handler.setFormatter(
        Formatter('\n%(asctime)s\n%(levelname)s\n%(message)s\n'))
    custom_logger.addHandler(handler)
    return custom_logger


LOGGER = get_root_logger()


def input_to_dict(user_input, date_format, /) -> dict:
    en_user_input = unquote(uninum2en(user_input))
    # Checking the user input for dot is important because
    # the use of dotless domains is prohibited.
    # See: https://features.icann.org/dotless-domains
    if '.' in en_user_input:
        # Try predefined URLs
        # Todo: The following code could be done in threads.
        if not (url_input := user_input.startswith('http')):
            url = 'http://' + user_input
        else:
            url = user_input
        parsed_url = urlparse(url)
        # TLD stands for top-level domain
        tldless_netloc = parsed_url[1].rpartition('.')[0].removeprefix('www.')
        # todo: make lazy?
        if (to_dict := TLDLESS_NETLOC_RESOLVER(tldless_netloc)) is not None:
            if to_dict is google_books_dict:
                return to_dict(parsed_url, date_format)
            elif to_dict is google_encrypted_dict:
                return to_dict(url, parsed_url, date_format)
            return to_dict(url, date_format)

        # DOIs contain dots
        if (m := DOI_SEARCH(unescape(en_user_input))) is not None:
            try:
                return doi_to_dict(m[0], True, date_format)
            except JSONDecodeError:
                if url_input is False:
                    raise
                # continue with urls_scr

        return urls_url_to_dict(url, date_format)
    else:
        # We can check user inputs containing dots for ISBNs, but probably is
        # error-prone.
        if (m := ISBN_10OR13_SEARCH(en_user_input)) is not None:
            try:
                return isbn_to_dict(m[0], True, date_format)
            except IsbnError:
                pass
        return UNDEFINED_INPUT_SCR


def app(environ: dict, start_response: callable) -> tuple:
    path_info = environ['PATH_INFO']
    if '/static/' in path_info:
        if path_info[-4:] == '.css':
            start_response('200 OK', CSS_HEADERS)
            return CSS,
        else:
            # path_info.endswith('.js') and config.lang == 'en'
            start_response('200 OK', JS_HEADERS)
            return JS,

    query_dict_get = parse_qs(environ['QUERY_STRING']).get
    date_format = query_dict_get('dateformat', [''])[0].strip()
    input_type = query_dict_get('input_type', [''])[0]

    # Warning: input is not escaped!
    if not (user_input := query_dict_get('user_input', [''])[0].strip()):
        response_body = scr_to_html(
            DEFAULT_SCR, date_format, input_type
        ).encode()
        RESPONSE_HEADERS['Content-Length'] = str(len(response_body))
        start_response('200 OK', RESPONSE_HEADERS.items())
        return response_body,

    to_dict = input_type_to_resolver[input_type]
    # noinspection PyBroadException
    try:
        d = to_dict(user_input, date_format)
    except RequestsConnectionError:
        status = '500 ConnectionError'
        LOGGER.exception(user_input)
        response_body = scr_to_html(HTTPERROR_SCR, date_format, input_type)
    except Exception as e:
        status = '500 Internal Server Error'

        if isinstance(e, ReturnError):
            scr = e.args
        else:
            LOGGER.exception(user_input)
            scr = OTHER_EXCEPTION_SCR

        response_body = scr_to_html(scr, date_format, input_type)
    else:
        scr = dict_to_sfn_cit_ref(d)
        status = '200 OK'
        response_body = scr_to_html(scr, date_format, input_type)
    response_body = response_body.encode()
    RESPONSE_HEADERS['Content-Length'] = str(len(response_body))
    start_response(status, RESPONSE_HEADERS.items())
    return response_body,


input_type_to_resolver = defaultdict(
    lambda: input_to_dict, {
        'url-doi-isbn': input_to_dict,  # todo: can be removed?
        'pmid': pmid_dict,
        'pmcid': pmcid_dict,
        'oclc': oclc_dict})


if __name__ == '__main__':
    # note that app.py is not run as '__main__' in kubernetes
    # only for local computer
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 5000, app)
    print('serving on http://localhost:5000')
    httpd.serve_forever()
