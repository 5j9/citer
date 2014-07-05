#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to ISBNs."""

import re
import urllib.request, urllib.error, urllib.parse

import langid

import bibtex
import adinebook
import config

if config.lang == 'en':
    import wikiref_en as wikiref
    import wikicite_en as wikicite
else:
    import wikiref_fa as wikiref
    import wikicite_fa as wikicite


#original regex from: https://www.debuggex.com/r/0Npla56ipD5aeTr9
isbn13_regex = re.compile(
    r'97(?:8|9)([ -]?)(?=\d{1,5}\1?\d{1,7}\1?\d{1,6}\1?\d)(?:\d\1*){9}\d'
    )
#original regex from: https://www.debuggex.com/r/2s3Wld3CVCR1wKoZ
isbn10_regex = re.compile(
    r'(?=\d{1,5}([ -]?)\d{1,7}\1?\d{1,6}\1?\d)(?:\d\1*){9}[\dX]'
    )
#original regex from: http://stackoverflow.com/a/14260708/2705757
isbn_regex = re.compile(
    r'(?=[-0-9 ]{17}|[-0-9X ]{13}|[0-9X]{10})(?:97[89][- ]?)\
?[0-9]{1,5}[- ]?(?:[0-9]+[- ]?){2}[0-9X]'
    )


class IsbnError(Exception):
    
    """Raise when bibliographic information is not available."""
    
    pass


class Citation():
    
    """Create isbn citation object."""

    def __init__(self, isbn_container_string, pure=False,
                 date_format='%Y-%m-%d'):
        """Get an ISBN-containing string and return an ISBN object."""
        if pure:
            self.isbn = isbn_container_string
        else:
            #search for isbn13
            m = re.search(isbn13_regex, isbn_container_string)
            if m:
                self.isbn = m.group(0)
            else:
                #search for isbn10
                m = re.search(isbn10_regex, isbn_container_string)
                self.isbn = m.group(0)
        adinebook_url = adinebook.isbn2url(self.isbn)
        a = adinebook.url2dictionary(adinebook_url)
        self.bibtex = ottobib(self.isbn)
        o = bibtex.parse(self.bibtex)
        self.dictionary = choose_dict(a, o)
        if not a and not o:
            raise IsbnError('Bibliographic information not found.')
        if 'language' in self.dictionary:
            self.error = 0
        else:
            self.dictionary['language'], self.dictionary['error'] =\
                                     langid.classify(self.dictionary['title'])
            self.error = round((1 - self.dictionary['error']) * 100, 2)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary, date_format)


def choose_dict(adinebook, ottobib):
    '''Choose which source to use.

Return adinebook if both sourses contain the same ISBN or if adinebook is None.
Background: adinebook.com ommits 3 digits from it's isbn when converting them to
urls. This may make them volnarable to resolving into wrong ISBN.
'''
    if adinebook and ottobib:
        #both exist
        if isbn2int(adinebook['isbn']) == isbn2int(ottobib['isbn']):
            #both isbns are equal
            return adinebook
        else:
            #isbns are not equal
            return ottobib
    elif adinebook:
        #only adinebook exists
        return adinebook
    else:
        #only ottobib exists
        return ottobib
    

def isbn2int(isbn):
    """Get ISBN string and return it as in integer."""
    isbn = isbn.replace('-', '')
    isbn = isbn.replace(' ', '')
    return int(isbn)


def ottobib(isbn):
    """Convert ISBN to bibtex using ottobib.com."""
    ottobib_url = 'http://www.ottobib.com/isbn/' + isbn + '/bibtex'
    ottobib_html = urllib.request.urlopen(ottobib_url).read().decode('utf8')
    m = re.search('<textarea.*>(.*)</textarea>', ottobib_html, re.DOTALL)
    bibtex = m.group(1)
    return bibtex
