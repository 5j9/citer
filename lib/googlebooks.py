#! /usr/bin/python
# -*- coding: utf-8 -*-

"""All things specifically related to the Google Books website."""


from urllib.parse import parse_qs
from urllib.parse import urlparse

from langid import classify
from requests import get as requests_get

# import bibtex [1]
from config import SPOOFED_USER_AGENT
from lib.ris import parse as ris_parse
from lib.commons import dict_to_sfn_cit_ref


def googlebooks_sfn_cit_ref(url, date_format='%Y-%m-%d') -> tuple:
    """Create the response namedtuple."""
    # bibtex_result = get_bibtex(url) [1]
    # dictionary = bibtex.parse(bibtex_result) [1]
    dictionary = ris_parse(get_ris(url))
    dictionary['date_format'] = date_format
    pu = urlparse(url)
    pq = parse_qs(pu.query)
    # default domain is prefered:
    dictionary['url'] = 'https://' + pu.netloc + '/books?id=' + pq['id'][0]
    # manually adding page number to dictionary:
    if 'pg' in pq:
        dictionary['page'] = pq['pg'][0][2:]
        dictionary['url'] += '&pg=' + pq['pg'][0]
    # although google does not provide a language field:
    if not dictionary['language']:
        dictionary['language'] = classify(dictionary['title'])[0]
    return dict_to_sfn_cit_ref(dictionary)


def get_bibtex(googlebook_url) -> bytes:
    """Get bibtex file content from a noormags url."""
    # getting id:
    pu = urlparse(googlebook_url)
    pq = parse_qs(pu.query)
    bookid = pq['id'][0]
    url = 'http://books.google.com/books/download/?id=' +\
          bookid + '&output=bibtex'
    # Agent spoofing is needed, otherwise: HTTP Error 401: Unauthorized
    return requests_get(
        url, headers={'User-agent': SPOOFED_USER_AGENT}, timeout=10
    ).content


def get_ris(googlebook_url):
    """Get ris file content from a noormags url."""
    # getting id:
    pu = urlparse(googlebook_url)
    pq = parse_qs(pu.query)
    bookid = pq['id'][0]
    url = 'http://books.google.com/books/download/?id=' +\
        bookid + '&output=ris'
    # Agent spoofing is needed, otherwise: HTTP Error 401: Unauthorized
    return requests_get(
        url, headers={'User-agent': SPOOFED_USER_AGENT}, timeout=10
    ).text
