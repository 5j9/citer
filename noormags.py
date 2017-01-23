#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to Noormags website."""

import re

import requests

import commons
import bibtex
import ris


class NoorMagsResponse(commons.BaseResponse):

    """Create noormags response object."""

    def __init__(self, noormags_url, date_format='%Y-%m-%d'):
        """Make the dictionary and run self.generate()."""
        self.date_format = date_format
        self.url = noormags_url
        self.bibtex = get_bibtex(noormags_url)
        self.dictionary = bibtex.parse(self.bibtex)
        # language parameter needs to be taken from RIS
        # other information are more accurate in bibtex
        # for example: http://www.noormags.com/view/fa/articlepage/104040
        # "IS  - 1" is wrong in RIS but "number = { 45 }," is correct in bibtex
        self.ris = get_ris(noormags_url)
        if 'LA' in self.ris:
            self.dictionary['language'] = ris.parse(self.ris)['language']
        self.generate()


def get_bibtex(noormags_url):
    """Get bibtex file content from a noormags_url. Return as string."""
    pagetext = requests.get(noormags_url).text
    article_id = re.search('/citation/bibtex/(\d+)', pagetext).group(1)
    url = 'http://www.noormags.ir/view/fa/citation/bibtex/' + article_id
    return requests.get(url).text


def get_ris(noormags_url):
    """Get ris file content from a noormags url. Return as string."""
    pagetext = requests.get(noormags_url).text
    article_id = re.search('/citation/ris/(\d+)', pagetext).group(1)
    url = 'http://www.noormags.ir/view/fa/citation/ris/' + article_id
    return requests.get(url).text
