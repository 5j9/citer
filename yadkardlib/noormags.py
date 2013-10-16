#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to Noormags website'''

import re
import urllib2

#import bibtex[1]
import ris
import reference
import citation

class NoorMag():
    '''A class to deal with noormags articles'''
    
    def __init__(self, noormags_url):
        self.url = noormags_url
        #self.bibtex = get_bibtex(noormags_url)[1]
        #self.dictionary = bibtex.parse(self.bibtex)[1]
        self.ris = get_ris(noormags_url)
        self.dictionary = ris.parse(self.ris) 
        self.ref = reference.create(self.dictionary)
        self.cite = citation.create(self.dictionary)
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
