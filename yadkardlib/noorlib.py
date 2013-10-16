#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to Noormags website'''

import re
import urllib2

import bibtex
#import ris[1]
import reference
import citation

class NoorLib():
    '''A class to deal with noormags articles'''
    
    def __init__(self, noormags_url):
        self.url = noormags_url
        self.bibtex = get_bibtex(noormags_url)
        self.dictionary = bibtex.parse(self.bibtex)
        #self.ris = get_ris(noormags_url)[1]
        #self.dictionary = ris.parse(self.ris)[1]
        self.ref = reference.create(self.dictionary)
        self.cite = citation.create(self.dictionary)
        self.error = 0

        
def get_bibtex(noormags_url):
    '''Gets bibtex file content from a noormags url'''
    pagetext = urllib2.urlopen(noormags_url).read()
    article_id = re.search('CitationHandler\.ashx\?id=(\d+)', pagetext).group(1)
    url = 'http://www.noorlib.ir/View/HttpHandler/CitationHandler.ashx?' +\
          'id=' + article_id + '&format=BibTex'
    bibtex = urllib2.urlopen(url).read()
    return bibtex

def get_ris(noormags_url):
    #This is copied from noormags module (currently not supported)[1]
    '''Gets bibtex file content from a noormags url'''
    pagetext = urllib2.urlopen(noormags_url).read()
    article_id = re.search('RIS&id=(\d+)', pagetext).group(1)
    url = 'http://www.noormags.com/view/CitationHandler.ashx?' +\
          'format=RIS&id=' + article_id
    ris = urllib2.urlopen(url).read()
    return ris
