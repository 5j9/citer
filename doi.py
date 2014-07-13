#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to DOI inputs."""


import re
import xml.sax.saxutils as sax

import requests

import commons
import bibtex


# regex from:
# http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
doi_regex = re.compile(r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)\b')


class Response(commons.BaseResponse):

    """Create a DOI's response object."""

    def __init__(self, doi_or_url, pure=False, date_format='%Y-%m-%d'):
        """Make the dictionary and run self.generate()."""
        self.date_format = date_format
        if pure:
            self.doi = doi_or_url
        else:
            # unescape '&amp;', '&lt;', and '&gt;' in doi_or_url
            unescaped_url = sax.unescape(doi_or_url)
            m = re.search(doi_regex, unescaped_url)
            if m:
                self.doi = m.group(1)
        self.url = 'http://dx.doi.org/' + self.doi
        self.bibtex = get_bibtex(self.url)
        self.dictionary = bibtex.parse(self.bibtex)
        if 'language' not in self.dictionary:
            if 'title' in self.dictionary:
                self.detect_language(self.dictionary['title'])
            else:
                self.error = 100
        self.generate()


def get_bibtex(doi_url):
    """Get BibTex file content from a DOI URL. Return as string."""
    r = requests.get(doi_url, headers={'Accept': 'application/x-bibtex'})
    bibtex = r.text
    return bibtex
