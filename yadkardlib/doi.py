#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to DOI inputs."""

import re
import urllib.request, urllib.error, urllib.parse
import xml.sax.saxutils as sax

import langid

from . import bibtex
from . import config

if config.lang == 'en':
    from . import wikiref_en as wikiref
    from . import wikicite_en as wikicite
else:
    from . import wikiref_fa as wikiref
    from . import wikicite_fa as wikicite


#regex from:
#http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
doi_regex = re.compile(r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)\b')


class Citation():
    
    """Create a DOI citation object."""
    
    def __init__(self, doi_or_url, pure=False, date_format='%Y-%m-%d'):
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
            if 'title' in self.dictionary:
                self.dictionary['language'], self.dictionary['error'] =\
                                             langid.classify(
                                                 self.dictionary['title'])
                self.error = round((1 - self.dictionary['error']) * 100, 2)
            else:
                self.error = 100
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary, date_format)


def get_bibtex(doi_url):
    """Get BibTex file content from a DOI URL. Return as string."""
    req = urllib.request.Request(doi_url)
    req.add_header('Accept', 'application/x-bibtex')
    bibtex = urllib.request.urlopen(req).read().decode('utf8')
    return bibtex

