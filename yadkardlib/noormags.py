#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to Noormags website'''

import re
import urllib2

import bibtex
import ris
import fawikiref
import fawikicite

class NoorMag():
    '''A class to deal with noormags articles'''
    
    def __init__(self, noormags_url):
        self.url = noormags_url
        self.bibtex = get_bibtex(noormags_url)
        self.dictionary = bibtex.parse(self.bibtex)
        #language parameter needs to be taken from RIS
        #other information are more accurate in bibtex
        #for example: http://www.noormags.com/view/fa/articlepage/104040
        #"IS  - 1" is wrong in RIS but "number = { 45 }," is correct in bibtex
        self.ris = get_ris(noormags_url)
        if 'LA' in self.ris:
            self.dictionary['language'] = ris.parse(self.ris)['language']
        self.ref = fawikiref.create(self.dictionary)
        self.cite = fawikicite.create(self.dictionary)
        self.error = 0

        
def get_bibtex(noormags_url):
    '''Gets bibtex file content from a noormags url'''
    pagetext = urllib2.urlopen(noormags_url).read()
    article_id = re.search('BibTex&id=(\d+)', pagetext).group(1)
    url = 'http://www.noormags.com/view/CitationHandler.ashx?' +\
          'format=BibTex&id=' + article_id
    bibtex = urllib2.urlopen(url).read()
    return bibtex

def get_ris(noormags_url):
    '''Gets bibtex file content from a noormags url'''
    pagetext = urllib2.urlopen(noormags_url).read()
    article_id = re.search('RIS&id=(\d+)', pagetext).group(1)
    url = 'http://www.noormags.com/view/CitationHandler.ashx?' +\
          'format=RIS&id=' + article_id
    ris = urllib2.urlopen(url).read()
    return ris
