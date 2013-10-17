#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to doi urls'''

import re
import urllib2
import xml.sax.saxutils as sax

import langid

import bibtex
import reference
import citation

class Doi():
    '''Creates a doi object'''
    
    def __init__(self, doi_or_url):
        #unescape '&amp;', '&lt;', and '&gt;' in doi_or_url befor applying regex
        unescaped_url = sax.unescape(doi_or_url)
        #it's assumed that there is always a match, this is (checked yadkard.py)
        self.doi = re.search(pattern, unescaped_url).group(1)
        self.url = 'http://dx.doi.org/' + self.doi
        self.bibtex = get_bibtex(self.url)
        print self.bibtex
        self.dictionary = bibtex.parse(self.bibtex)
        #although google does not provide a language field:
        if 'language' in self.dictionary:
            self.dictionary['language']
            self.error = 0
        else:
            self.dictionary['language'], self.dictionary['error'] =\
                                     detect_language(self.dictionary['title'])
            self.error = round((1 - self.dictionary['error']) * 100, 2)
        self.ref =reference.create(self.dictionary)
        self.cite = citation.create(self.dictionary)

def get_bibtex(doi_url):
    '''Gets bibtex file content from a doi url'''
    req = urllib2.Request(doi_url)
    req.add_header('Accept', 'text/bibliography; style=bibtex')
    bibtex = urllib2.urlopen(req).read()
    return bibtex

def detect_language(string):
    m = langid.classify(string)
    #langid.identifier.set_languages(['en','de','fr','es','ja','fa'])
    #m = langid.classify(string)
    language = m[0]
    error = m[1]
    return language, error

#pattern from:
#http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
pattern = re.compile(
                    r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)\b'
                    )
