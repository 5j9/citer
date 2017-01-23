#! /usr/bin/python
# -*- coding: utf-8 -*-

"""All things that are specifically related to adinebook website"""

import logging
import re

from requests import get as requests_get
from requests import RequestException
from bs4 import BeautifulSoup
from commons import Name, BaseResponse


ISBN_SEARCH = re.compile(r'شابک:.*?([\d-]*X?)</span></li>').search
YEAR_SEARCH = re.compile(r'نشر:</b>.*?\(.*?(\d\d\d\d)\)</li>').search
MONTH_SEARCH = re.compile(r'نشر:</b>.*\([\d\s]*(.*?)،.*').search
PUBLISHER_SEARCH = re.compile(r'نشر:</b>\s*(.*?)\s*\(.*</li>').search
TITLE_SEARCH = re.compile(
    r'آدینه بوک:\s*(?P<title>.*?)\s*~(?P<names>.*?)\s*$'
).search


class AdineBookResponse(BaseResponse):

    """Create Adinebook's response object."""

    def __init__(self, adinebook_url: str, date_format: str='%Y-%m-%d'):
        """Make the dictionary and run self.generate()."""
        self.date_format = date_format
        self.url = adinebook_url
        self.dictionary = url2dictionary(adinebook_url)
        if 'language' not in self.dictionary:
            # Assume that language is either fa or en.
            # Todo: give warning about this assumption.
            self.detect_language(self.dictionary['title'], {'en', 'fa'})
        self.generate()


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
        d = {'type': 'book'}
        bs = BeautifulSoup(adinebook_html, 'lxml')
        m = TITLE_SEARCH(bs.title.text)
        if m:
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
                editors.append(Name(name.partition('(ويراستار)')[0]))
            elif '(مترجم)' in name:
                translators.append(Name(name.partition('(مترجم)')[0]))
            elif '(' in name:
                other = Name(name.partition('(')[0])
                others.append(other)
                other.fullname = name
            else:
                authors.append(Name(name))
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
