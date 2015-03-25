#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to Noormags website."""

import re
import requests

import commons
import bibtex
# import ris[1]


class Response(commons.BaseResponse):

    """Create NoorLib response object."""

    def __init__(self, noorlib_url, date_format='%Y-%m-%d'):
        """Make the dictionary and run self.generate()."""
        self.date_format = date_format
        self.url = noorlib_url
        self.bibtex = get_bibtex(noorlib_url)
        self.dictionary = bibtex.parse(self.bibtex)
        #self.ris = get_ris(noorlib_url)[1]
        #self.dictionary = ris.parse(self.ris)[1]
        self.generate()


def get_bibtex(noorlib_url):
    """Get bibtex file content from a noormags url. Return as string."""
    pagetext = requests.get(noorlib_url).text
    article_id = re.search(
        'CitationHandler\.ashx\?id=(\d+)',
        pagetext,
    ).group(1)
    url = 'http://www.noorlib.ir/View/HttpHandler/CitationHandler.ashx?id=' +\
          article_id + '&format=BibTex'
    bibtex = requests.get(url).text
    return bibtex


def get_ris(noorlib_url):
    # This is copied from noormags module (currently not supported but may
    # be)[1]
    """Get ris file content from a noormags url. Return as string."""
    pagetext = requests.get(noorlib_url).text
    article_id = re.search('RIS&id=(\d+)', pagetext).group(1)
    url = 'http://www.noormags.com/view/CitationHandler.ashx?format=RIS&id=' +\
          article_id
    ris = requests.get(url).text
    return ris
