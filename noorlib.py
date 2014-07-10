#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to Noormags website."""

import re
import requests

import bibtex
import config
#import ris[1]

if config.lang == 'en':
    import sfn_en  as sfn
    import ctn_en as ctn
else:
    import sfn_fa as sfn
    import ctn_fa as ctn

class Response():

    """Create NoorLib citation object."""

    def __init__(self, noormags_url, date_format='%Y-%m-%d'):
        self.url = noormags_url
        self.bibtex = get_bibtex(noormags_url)
        self.dictionary = bibtex.parse(self.bibtex)
        #self.ris = get_ris(noormags_url)[1]
        #self.dictionary = ris.parse(self.ris)[1]
        self.sfnt = sfn.create(self.dictionary)
        self.ctnt = ctn.create(self.dictionary, date_format)
        self.error = 0


def get_bibtex(noormags_url):
    """Get bibtex file content from a noormags url. Return as string."""
    pagetext = requests.get(noormags_url).text
    article_id = re.search('CitationHandler\.ashx\?id=(\d+)', pagetext).group(1)
    url = 'http://www.noorlib.ir/View/HttpHandler/CitationHandler.ashx?' +\
          'id=' + article_id + '&format=BibTex'
    bibtex = requests.get(url).text
    return bibtex

def get_ris(noormags_url):
    #This is copied from noormags module (currently not supported but may be)[1]
    """Get ris file content from a noormags url. Return as string."""
    pagetext = requests.get(noormags_url).text
    article_id = re.search('RIS&id=(\d+)', pagetext).group(1)
    url = 'http://www.noormags.com/view/CitationHandler.ashx?' +\
          'format=RIS&id=' + article_id
    ris = requests.get(url).text
    return ris
