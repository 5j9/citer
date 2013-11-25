#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to ISBN'''

import re
import urllib2

import langid

import bibtex
import fawikiref
import fawikicite
import adinebook

class Isbn():
    '''Creates a isbn object'''

    def __init__(self, isbn_container_string, pure=False):
        '''gets an ISBN containing string and returns an ISBN onject
The digits parameter, if passed, should be 10 or 13.
'''
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
        if 'language' in self.dictionary:
            self.error = 0
        else:
            self.dictionary['language'], self.dictionary['error'] =\
                                     langid.classify(self.dictionary['title'])
            self.error = round((1 - self.dictionary['error']) * 100, 2)
        self.ref = fawikiref.create(self.dictionary)
        self.cite = fawikicite.create(self.dictionary)

def choose_dict(adinebook, ottobib):
    '''returns adinebook if both contain the same isbn or if adinebook is None.
Background: adinebook.com ommits 3 digits from it's isbn when converting them to
urls. This may make them volnarable to resolve for wrong isbn.'''
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
    isbn = isbn.replace('-', '')
    isbn = isbn.replace(' ', '')
    return int(isbn)

def ottobib(isbn):
    '''converts ISBN to bibtex using ottobib.com'''
    ottobib_url = 'http://www.ottobib.com/isbn/' + isbn + '/bibtex'
    ottobib_html = urllib2.urlopen(ottobib_url).read().decode('utf8')
    m = re.search('<textarea.*>(.*)</textarea>', ottobib_html, re.DOTALL)
    bibtex = m.group(1)
    return bibtex

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
