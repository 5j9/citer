#! /usr/bin/python
# -*- coding: utf-8 -*-

"""All things specifically related to the Google Books website."""


from urllib.parse import parse_qs
from urllib.parse import urlparse

from requests import get as requests_get

# import bibtex [1]
from ris import parse as ris_parse
from commons import BaseResponse


class GoogleBooksResponse(BaseResponse):

    """Create googlebooks' response object."""

    def __init__(self, url, date_format='%Y-%m-%d'):
        """Make the dictionary and run self.generate()."""
        # self.bibtex = get_bibtex(url) [1]
        # self.dictionary = bibtex.parse(self.bibtex) [1]
        self.bibtex = get_ris(url)
        dictionary = ris_parse(self.bibtex)
        dictionary['date_format'] = date_format
        self.dictionary = dictionary
        pu = urlparse(url)
        pq = parse_qs(pu.query)
        # default domain is prefered:
        dictionary['url'] = 'http://' + pu.netloc +\
                                 '/books?id=' + pq['id'][0]
        # manually adding page nubmer to dictionary:
        if 'pg' in pq:
            dictionary['pages'] = pq['pg'][0][2:]
            dictionary['url'] += '&pg=' + pq['pg'][0]
        # although google does not provide a language field:
        if 'language' not in dictionary:
            self.detect_language(dictionary['title'])
        self.generate()


def get_bibtex(googlebook_url):
    """Get bibtex file content from a noormags url."""
    # getting id:
    pu = urlparse(googlebook_url)
    pq = parse_qs(pu.query)
    bookid = pq['id'][0]
    url = 'http://books.google.com/books/download/?id=' +\
          bookid + '&output=bibtex'
    # Agent spoofing is needed, otherwise: HTTP Error 401: Unauthorized
    headers = {
        'User-agent':
        'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 '
        'Firefox/33.0'
    }
    bibtex = requests_get(url, headers=headers).text
    return bibtex


def get_ris(googlebook_url):
    """Get ris file content from a noormags url."""
    # getting id:
    pu = urlparse(googlebook_url)
    pq = parse_qs(pu.query)
    bookid = pq['id'][0]
    url = 'http://books.google.com/books/download/?id=' +\
        bookid + '&output=ris'
    # Agent spoofing is needed, otherwise: HTTP Error 401: Unauthorized
    headers = {
        'User-agent':
        'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 '
        'Firefox/33.0'
    }
    return requests_get(url, headers=headers).text
