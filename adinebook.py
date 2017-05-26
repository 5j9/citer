#! /usr/bin/python
# -*- coding: utf-8 -*-

"""All things that are specifically related to adinebook website"""

from collections import defaultdict
import logging
import re

from requests import get as requests_get, RequestException

from commons import RawName, dictionary_to_response, detect_language, Response


ISBN_SEARCH = re.compile(r'شابک:.*?([\d-]*X?)</span></li>').search
YEAR_SEARCH = re.compile(r'نشر:</b>.*?\(.*?(\d\d\d\d)\)</li>').search
MONTH_SEARCH = re.compile(r'نشر:</b>.*\([\d\s]*(.*?)،.*').search
PUBLISHER_SEARCH = re.compile(r'نشر:</b>\s*(.*?)\s*\(.*</li>').search
TITLE_SEARCH = re.compile(
    r'(?<=<title>آدینه بوک: )(?P<title>.*?)\s*~(?P<names>.*?)(?=\s*</title>)'
).search


def adinehbook_response(url: str, date_format: str= '%Y-%m-%d') -> Response:
    """Return the response namedtuple."""
    dictionary = url2dictionary(url)
    dictionary['date_format'] = date_format
    if 'language' not in dictionary:
        # Assume that language is either fa or en.
        # Todo: give warning about this assumption?
        dictionary['language'], dictionary['error'] = detect_language(
            dictionary['title'], ('en', 'fa')
        )
    return dictionary_to_response(dictionary)


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
        r = requests_get(adinebook_url, headers=headers)
        adinebook_html = r.content.decode('utf-8')
    except RequestException:
        logger.exception(adinebook_url)
        return
    if 'صفحه مورد نظر پبدا نشد.' in adinebook_html:
        return
    else:
        d = defaultdict(lambda: None, cite_type='book')
        m = TITLE_SEARCH(adinebook_html)
        d['title'] = m.group('title')
        names = m.group('names').split('،')
        # initiating name lists:
        others = []
        authors = []
        editors = []
        translators = []
        # building lists:
        for name in names:
            if '(ويراستار)' in name:
                editors.append(RawName(name.partition('(ويراستار)')[0]))
            elif '(مترجم)' in name:
                translators.append(RawName(name.partition('(مترجم)')[0]))
            elif '(' in name:
                other = RawName(name.partition('(')[0])
                others.append(other)
                other.fullname = name
            else:
                authors.append(RawName(name))
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
            d['publisher'] = m.group(1)
        m = MONTH_SEARCH(adinebook_html)
        if m:
            d['month'] = m.group(1)
        m = YEAR_SEARCH(adinebook_html)
        if m:
            d['year'] = m.group(1)
        m = ISBN_SEARCH(adinebook_html)
        if m:
            d['isbn'] = m.group(1)
    return d

logger = logging.getLogger(__name__)
