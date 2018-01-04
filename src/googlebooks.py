#! /usr/bin/python
# -*- coding: utf-8 -*-

"""All things specifically related to the Google Books website."""


from urllib.parse import parse_qs
from urllib.parse import urlparse

from langid import classify
from requests import get as requests_get

# import bibtex [1]
from src.ris import parse as ris_parse
from src.commons import dict_to_sfn_cit_ref


def googlebooks_sfn_cit_ref(url, date_format='%Y-%m-%d') -> tuple:
    """Create the response namedtuple."""
    # bibtex_result = get_bibtex(url) [1]
    # dictionary = bibtex.parse(bibtex_result) [1]
    dictionary = ris_parse(get_ris(url))
    dictionary['date_format'] = date_format
    pu = urlparse(url)
    pq = parse_qs(pu.query)
    # default domain is prefered:
    dictionary['url'] = 'http://' + pu.netloc + '/books?id=' + pq['id'][0]
    # manually adding page number to dictionary:
    if 'pg' in pq:
        dictionary['page'] = pq['pg'][0][2:]
        dictionary['url'] += '&pg=' + pq['pg'][0]
    # although google does not provide a language field:
    if not dictionary['language']:
        dictionary['language'] = classify(dictionary['title'])[0]
    return dict_to_sfn_cit_ref(dictionary)


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
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 '
        'Firefox/58.0'
    }
    bibtex = requests_get(url, headers=headers, timeout=10).text
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
    return requests_get(url, headers=headers, timeout=10).text
