#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to DOI inputs."""


import re
import html
import urllib.parse
import logging

import requests

import commons
import bibtex


# the regex is from:
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
            # decode percent encodings
            decoded_url = urllib.parse.unquote(html.unescape(doi_or_url))
            m = re.search(doi_regex, decoded_url)
            if m:
                self.doi = m.group(1)
        self.url = 'http://dx.doi.org/' + self.doi
        self.bibtex = get_bibtex(self.url)
        if self.bibtex == 'Resource not found.':
            logger.info('DOI could not be resolved.\n' + self.url)
            self.error = 100
            self.sfnt = 'DOI could not be resolved.'
            self.ctnt = self.bibtex
        else:
            self.dictionary = bibtex.parse(self.bibtex)
            self.generate()


def get_bibtex(doi_url):
    """Get BibTex file content from a DOI URL. Return as string."""
    r = requests.get(doi_url, headers={'Accept': 'application/x-bibtex'})
    bibtex = r.text
    return bibtex

logger = logging.getLogger(__name__)

