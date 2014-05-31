#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to Google Books'''

import re
import urllib2
from urlparse import parse_qs
from urlparse import urlparse

import langid

#import bibtex [1]
import ris
import config

if config.lang == 'en':
    import wikiref_en as wikiref
    import wikicite_en as wikicite
else:
    import wikiref_fa as wikiref
    import wikicite_fa as wikicite

class GoogleBook():
    '''Creates a google book object'''
    
    def __init__(self, googlebook_url):
        self.url = googlebook_url
        #self.bibtex = get_bibtex(googlebook_url) [1]
        #self.dictionary = bibtex.parse(self.bibtex) [1]
        self.bibtex = get_ris(googlebook_url)
        self.dictionary = ris.parse(self.bibtex)
        pu = urlparse(googlebook_url)
        pq = parse_qs(pu.query)
        #default domain is prefered:
        self.dictionary['url'] = 'http://' + pu.netloc +\
                                 '/books?id=' + pq['id'][0]
        #manually adding page nubmer to dictionary:
        if 'pg' in pq:
            self.dictionary['pages'] = pq['pg'][0][2:]
            self.dictionary['url'] += '&pg=' + pq['pg'][0]
        #although google does not provide a language field:
        if 'language' in self.dictionary:
            self.error = 0
        else:
            self.dictionary['language'], self.dictionary['error'] =\
                                     langid.classify(self.dictionary['title'])
            self.error = round((1 - self.dictionary['error']) * 100, 2)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)

def get_bibtex(googlebook_url):
    '''Gets bibtex file content from a noormags url'''
    #getting id:
    pu = urlparse(googlebook_url)
    pq = parse_qs(pu.query)
    bookid = pq['id'][0]
    url = 'http://books.google.com/books/download/?id=' +\
      bookid + '&output=bibtex'
    #Agent spoofing is needed, otherwise: HTTP Error 401: Unauthorized
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0)' +
                          ' Gecko/20100101 Firefox/24.0')]
    bibtex = opener.open(url).read().decode('utf8')
    return bibtex

def get_ris(googlebook_url):
    '''Gets bibtex file content from a noormags url'''
    #getting id:
    pu = urlparse(googlebook_url)
    pq = parse_qs(pu.query)
    bookid = pq['id'][0]
    url = 'http://books.google.com/books/download/?id=' +\
      bookid + '&output=ris'
    #Agent spoofing is needed, otherwise: HTTP Error 401: Unauthorized
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0)' +
                          ' Gecko/20100101 Firefox/24.0')]
    ris = opener.open(url).read().decode('utf8')
    return ris
