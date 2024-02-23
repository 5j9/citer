from io import BytesIO
from json import JSONDecodeError
from unittest.mock import Mock, patch
from urllib.parse import urlparse

# noinspection PyPackageRequirements
from pytest import raises

from app import (
    get_resolver,
    google_books_data,
    google_encrypted_data,
    input_type_to_resolver,
    logger,
    noorlib_data,
    noormags_data,
    root,
    url_doi_isbn_data,
)


def fake_resolver(*_):
    raise NotImplementedError


def assert_and_patch_resolver(url, resolver):
    d = get_resolver.__self__
    netloc = urlparse('http://' + url).netloc
    if netloc[:4] == 'www.':
        netloc = netloc[4:]
    tldless_netloc = netloc.rpartition('.')[0]
    assert d[tldless_netloc] == resolver
    return patch.dict(d, {tldless_netloc: fake_resolver})


def assert_scr(url, resolver):
    with assert_and_patch_resolver(url, resolver), raises(NotImplementedError):
        url_doi_isbn_data(url)


def assert_google_books_scr(url, resolver=google_books_data):
    assert_scr(url, resolver)


def test_google_books_netloc():
    ag = assert_google_books_scr
    # note that top level domains are ignored
    ag('encrypted.google.com/books?id=6upvonUt0O8C', google_encrypted_data)
    ag('books.google.com/books?id=pzmt3pcBuGYC')
    ag('books.google.de/books?id=pzmt3pcBuGYC')
    ag('books.google.com.ar/books?id=pzmt3pcBuGYC')
    ag('books.google.co.il/books?id=pzmt3pcBuGYC')
    with patch('app.google_books_data') as mock:
        url_doi_isbn_data('www.google.com/books?id=bwfoCAAAQBAJ')
        url_doi_isbn_data('www.google.com/books/edition/_/bwfoCAAAQBAJ')
    assert mock.call_count == 2


def assert_noormags_scr(url):
    assert_scr(url, noormags_data)


def test_noormags():
    an = assert_noormags_scr
    an('www.noormags.ir/view/fa/articlepage/105489/')
    an('www.noormags.net/view/fa/articlepage/105489/')
    an('noormags.ir/view/fa/articlepage/105489/')


def assert_noorlib_scr(url):
    assert_scr(url, noorlib_data)


def test_noorlib():
    an = assert_noorlib_scr
    an('www.noorlib.ir/View/fa/Book/BookView/Image/6120')
    an('www.noorlib.net/View/fa/Book/BookView/Image/6120')
    an('noorlib.ir/View/fa/Book/BookView/Image/6120')


@patch('app.url_data')
@patch('app.doi_data', side_effect=JSONDecodeError('msg', 'doc', 1))
def test_doi_url_fallback_to_url(doi_data, urls_data):
    user_input = 'https://dl.acm.org/doi/10.5555/3157382.3157535'
    assert url_doi_isbn_data(user_input) is urls_data.return_value
    doi_data.assert_called_once_with('10.5555/3157382.3157535', True)
    urls_data.assert_called_once_with(user_input)


def test_json_body():
    m = Mock(side_effect=NotImplementedError)
    with patch.dict(
        input_type_to_resolver,
        {
            'url-doi-isbn': m,
        },
    ), patch.object(logger, 'exception'):
        root(
            lambda _, __: None,
            {
                'CONTENT_LENGTH': '121',
                'wsgi.input': BytesIO(
                    b'{'
                    b'"user_input": "https://books.google.com/",'
                    b'"input_type": "url-doi-isbn",'
                    b'"dateformat": "%#d %B %Y"'
                    b'}'
                ),
            },
        )
    m.assert_called_once_with('https://books.google.com/')


def test_html_input():
    m = Mock(side_effect=NotImplementedError)
    with patch.dict(
        input_type_to_resolver,
        {
            'html': m,
        },
    ), patch.object(logger, 'exception'):
        root(
            lambda _, __: None,
            {
                'CONTENT_LENGTH': '121',
                'wsgi.input': BytesIO(
                    b'{'
                    b'"user_input": {"html": "<HTML>", "url": "<URL>"},'
                    b'"input_type": "html",'
                    b'"dateformat": "%#d %B %Y"'
                    b'}'
                ),
            },
        )
    m.assert_called_once_with({'html': '<HTML>', 'url': '<URL>'})


def test_invalid_user_input():
    with raises(ValueError):
        # the following used to return None
        # which ends up with unhandled error during convertion to scr tuple.
        url_doi_isbn_data('[object+HTMLInputElement]')
