#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to Noormags website."""

import re

from requests import get as requests_get

from commons import BaseResponse, dictionary_to_citations
from bibtex import parse as bibtex_parse
from ris import parse as ris_parse


class NoorMagsResponse(BaseResponse):

    """Create noormags response object."""

    def __init__(self, url, date_format='%Y-%m-%d'):
        """Make the dictionary and run self.generate()."""
        dictionary = bibtex_parse(get_bibtex(url))
        dictionary['date_format'] = date_format
        # language parameter needs to be taken from RIS
        # other information are more accurate in bibtex
        # for example: http://www.noormags.com/view/fa/articlepage/104040
        # "IS  - 1" is wrong in RIS but "number = { 45 }," is correct in bibtex
        self.ris = get_ris(url)
        if 'LA' in self.ris:
            dictionary['language'] = ris_parse(self.ris)['language']
        self.cite, self.sfn, self.ref = dictionary_to_citations(dictionary)


def get_bibtex(noormags_url):
    """Get bibtex file content from a noormags_url. Return as string."""
    pagetext = requests_get(noormags_url).text
    article_id = re.search('/citation/bibtex/(\d+)', pagetext).group(1)
    url = 'http://www.noormags.ir/view/fa/citation/bibtex/' + article_id
    return requests_get(url).text


def get_ris(noormags_url):
    """Get ris file content from a noormags url. Return as string."""
    pagetext = requests_get(noormags_url).text
    article_id = re.search('/citation/ris/(\d+)', pagetext).group(1)
    url = 'http://www.noormags.ir/view/fa/citation/ris/' + article_id
    return requests_get(url).text
