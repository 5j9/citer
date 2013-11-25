#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to doi urls'''

import re
import urllib2
import xml.sax.saxutils as sax

import langid

import bibtex
import fawikiref
import fawikicite

class Doi():
    '''Creates a doi object'''
    
    def __init__(self, doi_or_url, pure=False):
        if pure:
            self.doi = doi_or_url
        else:
            #unescape '&amp;', '&lt;', and '&gt;' in doi_or_url
            unescaped_url = sax.unescape(doi_or_url)
            m = re.search(doi_regex, unescaped_url)
            if m:
                self.doi = m.group(1)
        self.url = 'http://dx.doi.org/' + self.doi
        self.bibtex = get_bibtex(self.url)
        self.dictionary = bibtex.parse(self.bibtex)
        if 'language' in self.dictionary:
            self.error = 0
        else:
            self.dictionary['language'], self.dictionary['error'] =\
                                     langid.classify(self.dictionary['title'])
            self.error = round((1 - self.dictionary['error']) * 100, 2)
        self.ref =fawikiref.create(self.dictionary)
        self.cite = fawikicite.create(self.dictionary)

def get_bibtex(doi_url):
    '''Gets bibtex file content from a doi url'''
    req = urllib2.Request(doi_url)
    req.add_header('Accept', 'text/bibliography; style=bibtex')
    bibtex = urllib2.urlopen(req).read().decode('utf8')
    return bibtex

#regex from:
#http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
doi_regex = re.compile(
                    r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)\b'
                    )
