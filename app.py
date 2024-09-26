from collections.abc import Callable
from functools import partial
from html import unescape
from json import JSONDecodeError, dumps, loads
from urllib.parse import parse_qs, unquote, urlparse

from curl_cffi import CurlError

from lib import logger
from lib.archives import archive_org_data, archive_today_data
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
from lib.urls import MAX_RESPONSE_LENGTH, url_data, url_text


def google_encrypted_data(url, parsed_url) -> dict:
    if parsed_url[2][:7] in {'/books', '/books/'}:
        # sample urls:
        # https://encrypted.google.com/books?id=6upvonUt0O8C
        # https://www.google.com/books?id=bwfoCAAAQBAJ&pg=PA32
        # https://www.google.com/books/edition/_/bwfoCAAAQBAJ?gbpv=1&pg=PA32
        return google_books_data(parsed_url)
    return url_data(url)


get_resolver = {
    'archive': archive_today_data,
    'books.google': google_books_data,
    'books.google.co': google_books_data,
    'books.google.com': google_books_data,
    'encrypted.google': google_encrypted_data,
    'google': google_encrypted_data,
    'jstor': jstor_data,
    'ketab': ketabir_data,
    'noorlib': noorlib_data,
    'noormags': noormags_data,
    'web-beta.archive': archive_org_data,
    'web.archive': archive_org_data,
    'worldcat': worldcat_data,
}.get

http_headers = (
    ('Content-Type', 'text/html; charset=UTF-8'),
    ALLOW_ALL_ORIGINS,
)
json_headers = (
    ('Content-Type', 'application/json'),
    ALLOW_ALL_ORIGINS,
)


def html_data(user_input: dict):
    return url_data(user_input['url'], html=user_input['html'])


def url_doi_isbn_data(user_input: str, /) -> dict:
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
        hostname_core = parsed_url[1].rpartition('.')[0].removeprefix('www.')
        # todo: make lazy?
        if (data_func := get_resolver(hostname_core)) is not None:
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

    # We can check user inputs containing dots for ISBNs, but that sounds
    # error-prone.
    if (m := isbn_10or13_search(en_user_input)) is not None:
        return isbn_data(m[0], True)

    raise ValueError('invalid user_input')


BytesTuple = tuple[bytes]
StartResponse = Callable[[str, list[tuple[str, str]]], Callable]


def css(start_response: StartResponse, _) -> BytesTuple:
    start_response('200 OK', [*CSS_HEADERS])
    return (CSS,)


def js(start_response: StartResponse, _) -> BytesTuple:
    start_response('200 OK', [*JS_HEADERS])
    return (JS,)


def page_does_not_exist(start_response: StartResponse, _) -> BytesTuple:
    start_response(
        '404 not found',
        [
            ('Content-Type', 'text/plain'),
        ],
    )
    return (b'404 not found',)


def echo(url: str, _: str, /):
    try:
        url, text = url_text(url)
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
    'html': html_data,
}


def read_body(environ: dict, /) -> bytes:
    length = int(environ.get('CONTENT_LENGTH') or 0)
    if length > MAX_RESPONSE_LENGTH:
        logger.error(f'CONTENT_LENGTH was too long; {length:,} bytes')
        return b''  # do not process the input
    return environ['wsgi.input'].read(length)


def parse_params(
    environ: dict,
) -> tuple[
    str,
    str,
    str,
    str | dict,  # user_input is dict when input_type == html
    list[tuple[str, str]],
    Callable[[tuple[str, str, str]], str],
]:
    body = read_body(environ)
    if body:
        get = loads(body).get
        return (
            get('dateformat') or '%Y-%m-%d',
            get('pipeformat') or ' | ',
            get('input_type', ''),
            get('user_input', ''),  # string user_input is trimmed in common.js
            [*json_headers],
            dumps,
        )

    query_get = parse_qs(environ['QUERY_STRING']).get
    date_format = query_get('dateformat', ('%Y-%m-%d',))[0].strip()
    pipe_format = query_get('pipeformat', [' | '])[0].replace('+', ' ')
    input_type = query_get('input_type', ('',))[0]
    return (
        date_format,
        pipe_format,
        input_type,
        query_get('user_input', ('',))[0].strip(),
        # for the bookmarklet; also if user directly goes to query page
        [*http_headers],
        partial(
            scr_to_html,
            date_format=date_format,
            pipe_format=pipe_format,
            input_type=input_type,
        ),
    )


def root(start_response: StartResponse, environ: dict) -> BytesTuple:
    (
        date_format,
        pipe_format,
        input_type,
        user_input,
        headers,
        scr_to_resp_body,
    ) = parse_params(environ)
    if not user_input:
        response_body = scr_to_html(
            DEFAULT_SCR, date_format, pipe_format, input_type
        ).encode()
        start_response('200 OK', [*http_headers])
        return (response_body,)

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
        scr = data_to_sfn_cit_ref(d, date_format, pipe_format)
        status = '200 OK'

    response_body = scr_to_resp_body(scr).encode()
    start_response(status, headers)
    return (response_body,)


get_handler: Callable[[str], Callable[[StartResponse, dict], BytesTuple]] = {
    f'/{CSS_PATH}.css': css,
    f'/{JS_PATH}.js': js,
    '/': root,
    '/citer.fcgi': root,  # for backward compatibility
}.get  # type: ignore


def app(environ: dict, start_response: StartResponse) -> BytesTuple:
    # noinspection PyBroadException
    try:
        return (get_handler(environ['PATH_INFO']) or page_does_not_exist)(
            start_response, environ
        )
    except Exception:
        start_response('500 Internal Server Error', [])
        logger.exception('app error, environ:\n%s', environ)
        return (b'Unknown Error',)


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
