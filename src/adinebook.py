#! /usr/bin/python
# -*- coding: utf-8 -*-

"""All things that are specifically related to adinebook website"""

from collections import defaultdict
import logging

from langid import classify
from regex import compile as regex_compile
from requests import get as requests_get, RequestException

from src.commons import first_last, dict_to_sfn_cit_ref


ISBN_SEARCH = regex_compile(
    r'<meta property="book:isbn" content="([^"]++)'
).search
DATE_SEARCH = regex_compile(
    r'تاریخ نشر:</span>\s*+'
    r'(?:(?<day>\d\d?)? (?<month>[^،]*+)، )?(?<year>\d{4})'
).search
PUBLISHER_SEARCH = regex_compile(
    r'ناشر:(?:<[^>]++>\s*)++([^<\n]++)'
).search
TITLE_SEARCH = regex_compile(
    r'<meta property="og:title" content="([^"]++)'
).search
AUTHORS_SEARCH = regex_compile(
    r'<meta property="book:author" content=" *+~([^"]++)'
).search


def adinehbook_sfn_cit_ref(url: str, date_format='%Y-%m-%d') -> tuple:
    """Return the response namedtuple."""
    dictionary = url2dictionary(url)
    dictionary['date_format'] = date_format
    if 'language' not in dictionary:
        # Assume that language is either fa or en.
        # Todo: give warning about this assumption?
        dictionary['language'] = \
            classify(dictionary['title'])[0]
    return dict_to_sfn_cit_ref(dictionary)


def isbn2url(isbn: str):
    """Convert isbn to AdinebookURL. Return the url as string."""
    # Apparently adinebook uses 10 digit codes (without hyphens) for its
    # book-urls. If it's an isbn13 then the first 3 digits are excluded
    isbn = isbn.replace('-', '').replace(' ', '')
    if len(isbn) == 13:
        isbn = isbn[3:]
    url = 'http://www.adinebook.com/gp/product/' + isbn
    return url


def url2dictionary(adinebook_url: str):
    """Get adinebook_url and return the result as a dict."""
    try:
        # Try to see if adinebook is available,
        # ottobib should continoue its work in isbn.py if it is not.
        headers = {
            'User-agent':
            'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) '
            'Gecko/20100101 Firefox/33.0'
        }
        r = requests_get(adinebook_url, headers=headers, timeout=10)
        adinebook_html = r.content.decode('utf-8')
    except RequestException:
        logger.exception(adinebook_url)
        return
    if 'صفحه مورد نظر پبدا نشد.' in adinebook_html:
        return
    else:
        d = defaultdict(lambda: None, cite_type='book')
        d['title'] = TITLE_SEARCH(adinebook_html)[1]
        # initiating name lists:
        others = []
        authors = []
        editors = []
        translators = []
        # building lists:
        for name in AUTHORS_SEARCH(adinebook_html)[1].strip().split('،'):
            if '(به اهتمام)' in name:
                authors.append(first_last(name.partition('(به اهتمام)')[0]))
            elif '(ویراستار)' in name:
                editors.append(first_last(name.partition('(ویراستار)')[0]))
            elif '(مترجم)' in name:
                translators.append(first_last(name.partition('(مترجم)')[0]))
            elif '(' in name:
                others.append(('', name))
            else:
                authors.append(first_last(name))
        if authors:
            d['authors'] = authors
        if others:
            d['others'] = others
        if editors:
            d['editors'] = editors
        if translators:
            d['translators'] = translators
        m = PUBLISHER_SEARCH(adinebook_html)
        if m:
            d['publisher'] = m[1]
        m = DATE_SEARCH(adinebook_html)
        if m:
            d['month'] = m['month']
            d['year'] = m['year']
        m = ISBN_SEARCH(adinebook_html)
        if m:
            d['isbn'] = m[1]
    return d


logger = logging.getLogger(__name__)
