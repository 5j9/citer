from unittest import TestCase, main
from unittest.mock import patch

from app import (
    url_doi_isbn_scr, TLDLESS_NETLOC_RESOLVER, google_com_scr, googlebooks_scr,
    noormags_scr, noorlib_scr
)


def fake_resolver(*_):
    raise NotImplementedError


def assert_and_patch_resolver_dict(netloc, resolver):
    d = TLDLESS_NETLOC_RESOLVER.__self__
    if netloc[:4] == 'www.':
        netloc = netloc[4:]
    tldless_netloc = netloc.rpartition('.')[0]
    assert d[tldless_netloc] == resolver
    return patch.dict(d, {tldless_netloc: fake_resolver})


class TestURLHandler(TestCase):

    def assert_scr(self, fmt, netloc, resolver):
        with assert_and_patch_resolver_dict(netloc, resolver):
            self.assertRaises(
                NotImplementedError, url_doi_isbn_scr, fmt.format(netloc),
                '%Y-%m-%d')

    def assert_google_books_scr(self, netloc, resolver=googlebooks_scr):
        self.assert_scr('https://{}/books?id=6upvonUt0O8C', netloc, resolver)

    def test_google_books(self):
        asrt = self.assert_google_books_scr
        # note that top level domains are ignored
        asrt('encrypted.google.com', google_com_scr)
        asrt('books.google.com')
        asrt('books.google.de')
        asrt('books.google.com.ar')
        asrt('books.google.co.il')

    def assert_noormags_scr(self, netloc):
        self.assert_scr(
            'http://{}/view/fa/articlepage/1234', netloc, noormags_scr)

    def test_noormags(self):
        an = self.assert_noormags_scr
        an('www.noormags.ir')
        an('noormags.ir')
        an('www.noormags.net')

    def assert_noorlib_scr(self, netloc):
        self.assert_scr(
            'https://{}/View/fa/Book/BookView/Image/6120', netloc, noorlib_scr)

    def test_noorlib(self):
        an = self.assert_noorlib_scr
        an('www.noorlib.ir')
        an('noorlib.ir')
        an('www.noorlib.net')


if __name__ == '__main__':
    main()
