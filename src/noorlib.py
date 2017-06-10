#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to Noormags website."""

import re

from requests import get as requests_get

from src.commons import dictionary_to_response, Response
from src.bibtex import parse as bibtex_parse
# import ris[1]


def noorlib_response(url: str, date_format: str= '%Y-%m-%d') -> Response:
    """Create the response namedtuple."""
    dictionary = bibtex_parse(get_bibtex(url))
    dictionary['date_format'] = date_format
    # risr = get_ris(url)[1]
    # dictionary = risr.parse(ris)[1]
    return dictionary_to_response(dictionary)


def get_bibtex(noorlib_url):
    """Get bibtex file content from a noormags url. Return as string."""
    pagetext = requests_get(noorlib_url).text
    article_id = re.search(
        'CitationHandler\.ashx\?id=(\d+)',
        pagetext,
    ).group(1)
    url = 'http://www.noorlib.ir/View/HttpHandler/CitationHandler.ashx?id=' +\
          article_id + '&format=BibTex'
    return requests_get(url).text


def get_ris(noorlib_url):
    # This is copied from noormags module (currently not supported but may
    # be)[1]
    """Get ris file content from a noormags url. Return as string."""
    pagetext = requests_get(noorlib_url).text
    article_id = re.search('RIS&id=(\d+)', pagetext).group(1)
    url = 'http://www.noormags.com/view/CitationHandler.ashx?format=RIS&id=' +\
          article_id
    return requests_get(url).text
