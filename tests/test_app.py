from unittest.mock import patch
from urllib.parse import urlparse

# noinspection PyPackageRequirements
from pytest import raises
from requests import JSONDecodeError

from app import (
    TLDLESS_NETLOC_RESOLVER,
    google_books_dict,
    google_encrypted_dict,
    noorlib_url_to_dict,
    noormags_url_to_dict,
    url_doi_isbn_to_dict,
)


def fake_resolver(*_):
    raise NotImplementedError


def assert_and_patch_resolver(url, resolver):
    d = TLDLESS_NETLOC_RESOLVER.__self__
    netloc = urlparse('http://' + url).netloc
    if netloc[:4] == 'www.':
        netloc = netloc[4:]
    tldless_netloc = netloc.rpartition('.')[0]
    assert d[tldless_netloc] == resolver
    return patch.dict(d, {tldless_netloc: fake_resolver})


def assert_scr(url, resolver):
    with assert_and_patch_resolver(url, resolver), raises(NotImplementedError):
        url_doi_isbn_to_dict(url, '%Y-%m-%d')


def assert_google_books_scr(url, resolver=google_books_dict):
    assert_scr(url, resolver)


def test_google_books_netloc():
    ag = assert_google_books_scr
    # note that top level domains are ignored
    ag('encrypted.google.com/books?id=6upvonUt0O8C', google_encrypted_dict)
    ag('books.google.com/books?id=pzmt3pcBuGYC')
    ag('books.google.de/books?id=pzmt3pcBuGYC')
    ag('books.google.com.ar/books?id=pzmt3pcBuGYC')
    ag('books.google.co.il/books?id=pzmt3pcBuGYC')
    with patch('app.google_books_dict') as mock:
        url_doi_isbn_to_dict('www.google.com/books?id=bwfoCAAAQBAJ', None)
        url_doi_isbn_to_dict('www.google.com/books/edition/_/bwfoCAAAQBAJ', None)
    assert mock.call_count == 2


def assert_noormags_scr(url):
    assert_scr(url, noormags_url_to_dict)


def test_noormags():
    an = assert_noormags_scr
    an('www.noormags.ir/view/fa/articlepage/105489/')
    an('www.noormags.net/view/fa/articlepage/105489/')
    an('noormags.ir/view/fa/articlepage/105489/')


def assert_noorlib_scr(url):
    assert_scr(url, noorlib_url_to_dict)


def test_noorlib():
    an = assert_noorlib_scr
    an('www.noorlib.ir/View/fa/Book/BookView/Image/6120')
    an('www.noorlib.net/View/fa/Book/BookView/Image/6120')
    an('noorlib.ir/View/fa/Book/BookView/Image/6120')


@patch('app.urls_url_to_dict')
@patch('app.doi_to_dict', side_effect=JSONDecodeError('msg', 'doc', 1))
def test_doi_url_fallback_to_url(doi_scr, urls_scr):
    user_input = 'https://dl.acm.org/doi/10.5555/3157382.3157535'
    assert url_doi_isbn_to_dict(user_input, '%B %#d, %Y') is urls_scr.return_value
    doi_scr.assert_called_once_with('10.5555/3157382.3157535', True, '%B %#d, %Y')
    urls_scr.assert_called_once_with(user_input, '%B %#d, %Y')
