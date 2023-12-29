from functools import partial
from html import unescape
from json import JSONDecodeError, dumps
from logging import INFO, Formatter, basicConfig, getLogger
from logging.handlers import RotatingFileHandler
from os.path import abspath, dirname
from urllib.parse import parse_qs, unquote, urlparse

from lib.commons import (
    ReturnError,
    dict_to_sfn_cit_ref,
    isbn_10or13_search,
    uninum2en,
)
from lib.doi import doi_search, doi_to_dict
from lib.googlebooks import url_to_dict as google_books_dict
from lib.html import (
    CSS,
    CSS_HEADERS,
    CSS_PATH,
    DEFAULT_SCR,
    JS,
    JS_HEADERS,
    JS_PATH,
    scr_to_html,
)
from lib.isbn_oclc import isbn_to_dict, oclc_dict, worldcat_url_to_dict
from lib.jstor import url_to_dict as jstor_url_to_dict
from lib.ketabir import url_to_dict as ketabir_url_to_dict
from lib.noorlib import url_to_dict as noorlib_url_to_dict
from lib.noormags import url_to_dict as noormags_url_to_dict
from lib.pubmed import pmcid_dict, pmid_dict
from lib.urls import get_html, url_to_dict as urls_url_to_dict
from lib.waybackmachine import url_to_dict as archive_url_to_dict


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

# always assign 'Content-Length' header HTTP_HEADERS[1] before sending
HTTP_HEADERS = [('Content-Type', 'text/html; charset=UTF-8'), None]
JSON_HEADERS = [('Content-Type', 'application/json'), None]


def get_logger():
    basicConfig(
        format='%(pathname)s:%(lineno)d\n%(asctime)s %(levelname)s %(message)s'
    )
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    src_dir = dirname(abspath(__file__))
    handler = RotatingFileHandler(
        filename=f'{src_dir}/citer.log',
        mode='a',
        maxBytes=20000,
        backupCount=0,
        encoding='utf-8',
    )
    handler.setLevel(INFO)
    handler.setFormatter(
        Formatter('\n%(asctime)s\n%(levelname)s\n%(message)s\n')
    )
    logger.addHandler(handler)
    return logger


LOGGER = get_logger()


def url_doi_isbn_to_dict(user_input, date_format, /) -> dict:
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
        if (m := doi_search(unescape(en_user_input))) is not None:
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
        if (m := isbn_10or13_search(en_user_input)) is not None:
            return isbn_to_dict(m[0], True, date_format)


def css(start_response: callable, *_) -> tuple:
    start_response('200 OK', CSS_HEADERS)
    return (CSS,)


def js(start_response: callable, *_) -> tuple:
    start_response('200 OK', JS_HEADERS)
    return (JS,)


def page_does_not_exist(start_response: callable, *_) -> tuple:
    text = b'404 not found'
    start_response(
        '404 not found',
        [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(text))),
        ],
    )
    return (text,)


def echo(url: str, _: str, /):
    try:
        url, text = get_html(url)
    except Exception as e:
        url, text = type(e).__name__, ''
    raise ReturnError(url, '', text)


input_type_to_resolver = {
    '': url_doi_isbn_to_dict,
    'url-doi-isbn': url_doi_isbn_to_dict,
    'pmid': pmid_dict,
    'pmcid': pmcid_dict,
    'oclc': oclc_dict,
    'echo': echo,
}


def read_body(environ: dict, /):
    length = int(environ.get('CONTENT_LENGTH') or 0)
    if length > 10_000:
        LOGGER.error(f'CONTENT_LENGTH was too long; {length=} bytes')
        return ''  # do not process the input
    return environ['wsgi.input'].read(length).decode()


def root(start_response: callable, environ: dict) -> tuple:
    query_get = parse_qs(environ['QUERY_STRING']).get
    date_format = query_get('dateformat', ['%Y-%m-%d'])[0].strip()
    input_type = query_get('input_type', [''])[0]

    # Warning: input is not escaped!
    body = read_body(environ)
    if not (user_input := (body or query_get('user_input', [''])[0]).strip()):
        response_body = scr_to_html(
            DEFAULT_SCR, date_format, input_type
        ).encode()
        HTTP_HEADERS[1] = ('Content-Length', str(len(response_body)))
        start_response('200 OK', HTTP_HEADERS)
        return (response_body,)

    if body:
        headers = JSON_HEADERS
        scr_to_resp_body = dumps
    else:  # for the bookmarklet; also if user directly goes to query page
        headers = HTTP_HEADERS
        scr_to_resp_body = partial(
            scr_to_html, date_format=date_format, input_type=input_type
        )

    to_dict = input_type_to_resolver[input_type]

    try:
        d = to_dict(user_input, date_format)
    except Exception as e:
        status = '500 Internal Server Error'

        if isinstance(e, ReturnError):
            scr = e.args
        else:
            LOGGER.exception(user_input)
            scr = type(e).__name__, '', ''
    else:
        scr = dict_to_sfn_cit_ref(d)
        status = '200 OK'

    response_body = scr_to_resp_body(scr).encode()
    headers[1] = ('Content-Length', str(len(response_body)))
    start_response(status, headers)
    return (response_body,)


PATH_TO_HANDLER = {
    f'/{CSS_PATH}.css': css,
    f'/{JS_PATH}.js': js,
    '/': root,
    '/citer.fcgi': root,  # for backward compatibility
}.get


def app(environ: dict, start_response: callable) -> tuple:
    return (PATH_TO_HANDLER(environ['PATH_INFO']) or page_does_not_exist)(
        start_response, environ
    )


if __name__ == '__main__':
    # note that app.py is not run as '__main__' in kubernetes
    # only for local computer
    from wsgiref.simple_server import make_server

    httpd = make_server('localhost', 5000, app)
    print('serving on http://localhost:5000')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
