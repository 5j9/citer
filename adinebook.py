#! /usr/bin/python
# -*- coding: utf-8 -*-

"""All things that are specifically related to adinebook website"""

import logging
from re import search, split

import requests
from requests import RequestException
from bs4 import BeautifulSoup

from commons import Name, BaseResponse


class Response(BaseResponse):

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
        r = requests.get(adinebook_url, headers=headers)
        adinebook_html = r.content.decode('utf-8')
    except RequestException:
        logger.exception(adinebook_url)
        return
    if 'صفحه مورد نظر پبدا نشد.' in adinebook_html:
        return
    else:
        d = {'type': 'book'}
        bs = BeautifulSoup(adinebook_html, 'lxml')
        m = search(
            'آدینه بوک:\s*(?P<title>.*?)\s*~(?P<names>.*?)\s*$',
            bs.title.text,
        )
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
                editors.append(Name(name.split('(ويراستار)')[0]))
            elif '(مترجم)' in name:
                translators.append(Name(name.split('(مترجم)')[0]))
            elif '(' in name:
                other = Name(split('\(.*\)', name)[0])
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
        m = search('نشر:</b>\s*(.*?)\s*\(.*</li>', adinebook_html)
        if m:
            d['publisher'] = m.group(1)
        m = search('نشر:</b>.*\([\d\s]*(.*?)،.*', adinebook_html)
        if m:
            d['month'] = m.group(1)
        m = search('نشر:</b>.*?\(.*?(\d\d\d\d)\)</li>', adinebook_html)
        if m:
            d['year'] = m.group(1)
        m = search('شابک:.*?([\d-]*X?)</span></li>', adinebook_html)
        if m:
            d['isbn'] = m.group(1)
    return d

logger = logging.getLogger(__name__)
