#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to DOI inputs."""


import re
from urllib.parse import unquote
import logging
from html import unescape

from requests import get as requests_get

from commons import BaseResponse
from config import lang
from bibtex import parse as bibtex_parse


# The regex is from:
# http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
DOI_SEARCH = re.compile(
    r'\b(10\.[0-9]{4,}(?:\.[0-9]+)*/(?:(?!["&\'])\S)+)\b'
).search


class DoiResponse(BaseResponse):

    """Create a DOI's response object."""

    def __init__(self, doi_or_url, pure=False, date_format='%Y-%m-%d'):
        """Make the dictionary and run self.generate()."""
        self.date_format = date_format
        if pure:
            self.doi = doi_or_url
        else:
            # unescape '&amp;', '&lt;', and '&gt;' in doi_or_url
            # decode percent encodings
            decoded_url = unquote(unescape(doi_or_url))
            m = DOI_SEARCH(decoded_url)
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
            self.dictionary = bibtex_parse(self.bibtex)
            if lang == 'fa':
                self.detect_language(self.dictionary['title'])
            self.generate()


def get_bibtex(doi_url):
    """Get BibTex file content from a DOI URL. Return as string."""
    return requests_get(
        doi_url, headers={'Accept': 'application/x-bibtex'}
    ).text

logger = logging.getLogger(__name__)

