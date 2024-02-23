from functools import partial
from html import unescape
from json import JSONDecodeError, dumps
from urllib.parse import parse_qs, unquote, urlparse

from curl_cffi import CurlError

from lib import logger
from lib.archives import archive_org_data
from lib.commons import (
    ReturnError,
    data_to_sfn_cit_ref,
    isbn_10or13_search,
    uninum2en,
)
from lib.doi import doi_data, doi_search
from lib.googlebooks import google_books_data
from lib.html import (
    ALLOW_ALL_ORIGINS,
    CSS,
    CSS_HEADERS,
    CSS_PATH,
    DEFAULT_SCR,
    JS,
    JS_HEADERS,
    JS_PATH,
    scr_to_html,
)
from lib.isbn_oclc import isbn_data, oclc_data, worldcat_data
from lib.jstor import jstor_data
from lib.ketabir import ketabir_data
from lib.noorlib import noorlib_data
from lib.noormags import noormags_data
from lib.pubmed import pmcid_data, pmid_data
from lib.urls import get_html, url_data


def google_encrypted_data(url, parsed_url) -> dict:
    if parsed_url[2][:7] in {'/books', '/books/'}:
        # sample urls:
        # https://encrypted.google.com/books?id=6upvonUt0O8C
        # https://www.google.com/books?id=bwfoCAAAQBAJ&pg=PA32
        # https://www.google.com/books/edition/_/bwfoCAAAQBAJ?gbpv=1&pg=PA32
        return google_books_data(parsed_url)
    return url_data(url)


TLDLESS_NETLOC_RESOLVER = {
    'ketab': ketabir_data,
    'worldcat': worldcat_data,
    'noorlib': noorlib_data,
    'noormags': noormags_data,
    'web.archive': archive_org_data,
    'web-beta.archive': archive_org_data,
    'books.google.co': google_books_data,
    'books.google.com': google_books_data,
    'books.google': google_books_data,
    'google': google_encrypted_data,
    'encrypted.google': google_encrypted_data,
    'jstor': jstor_data,
}.get

# Always assign 'Content-Length' header to HTTP_HEADERS[0] before sending.
http_headers = [
    None,
    ('Content-Type', 'text/html; charset=UTF-8'),
    ALLOW_ALL_ORIGINS,
]
json_headers = [
    None,
    ('Content-Type', 'application/json'),
    ALLOW_ALL_ORIGINS,
]


def url_doi_isbn_data(user_input, /) -> dict:
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
        if (data_func := TLDLESS_NETLOC_RESOLVER(tldless_netloc)) is not None:
            if data_func is google_books_data:
                return data_func(parsed_url)
            elif data_func is google_encrypted_data:
                return data_func(url, parsed_url)
            return data_func(url)

        # DOIs contain dots
        if (m := doi_search(unescape(en_user_input))) is not None:
            try:
                return doi_data(m[0], True)
            except JSONDecodeError:
                if url_input is False:
                    raise
                # continue with urls_scr

        return url_data(url)
    else:
        # We can check user inputs containing dots for ISBNs, but probably is
        # error-prone.
        if (m := isbn_10or13_search(en_user_input)) is not None:
            return isbn_data(m[0], True)


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
    '': url_doi_isbn_data,
    'url-doi-isbn': url_doi_isbn_data,
    'pmid': pmid_data,
    'pmcid': pmcid_data,
    'oclc': oclc_data,
    'echo': echo,
}


def read_body(environ: dict, /):
    length = int(environ.get('CONTENT_LENGTH') or 0)
    if length > 10_000:
        logger.error(f'CONTENT_LENGTH was too long; {length=} bytes')
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
        http_headers[0] = ('Content-Length', str(len(response_body)))
        start_response('200 OK', http_headers)
        return (response_body,)

    if body:
        headers = json_headers
        scr_to_resp_body = dumps
    else:  # for the bookmarklet; also if user directly goes to query page
        headers = http_headers
        scr_to_resp_body = partial(
            scr_to_html, date_format=date_format, input_type=input_type
        )

    data_func = input_type_to_resolver[input_type]

    try:
        d = data_func(user_input)
    except Exception as e:
        status = '500 Internal Server Error'

        if isinstance(e, ReturnError):
            scr = e.args
        else:
            if not isinstance(e, CurlError):
                logger.exception(user_input)
            scr = type(e).__name__, '', ''
    else:
        scr = data_to_sfn_cit_ref(d, date_format)
        status = '200 OK'

    response_body = scr_to_resp_body(scr).encode()
    headers[0] = ('Content-Length', str(len(response_body)))
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
