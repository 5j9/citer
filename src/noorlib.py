#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to Noormags website."""

from re import compile as re_compile

from requests import get as requests_get

from src.commons import dict_to_sfn_cit_ref
from src.bibtex import parse as bibtex_parse


BIBTEX_ARTICLE_ID_SEARCH = re_compile(
    '(?<=CitationHandler\.ashx\?id=)\d+'
).search
RIS_ARTICLE_ID_SEARCH = re_compile('(?<=RIS&id=)\d+').search


def noorlib_sfn_cit_ref(url: str, date_format: str= '%Y-%m-%d') -> tuple:
    """Create the response namedtuple."""
    dictionary = bibtex_parse(get_bibtex(url))
    dictionary['date_format'] = date_format
    # risr = get_ris(url)[1]
    # dictionary = risr.parse(ris)[1]
    return dict_to_sfn_cit_ref(dictionary)


def get_bibtex(noorlib_url):
    """Get bibtex file content from a noormags url. Return as string."""
    pagetext = requests_get(noorlib_url, timeout=10).text
    article_id = BIBTEX_ARTICLE_ID_SEARCH(pagetext)[0]
    url = 'http://www.noorlib.ir/View/HttpHandler/CitationHandler.ashx?id=' +\
          article_id + '&format=BibTex'
    return requests_get(url, timeout=10).text


def get_ris(noorlib_url):
    # This is copied from noormags module (currently not supported but may
    # be)[1]
    """Get ris file content from a noormags url. Return as string."""
    pagetext = requests_get(noorlib_url, timeout=10).text
    article_id = RIS_ARTICLE_ID_SEARCH(pagetext)[0]
    url = 'http://www.noormags.com/view/CitationHandler.ashx?format=RIS&id=' +\
          article_id
    return requests_get(url, timeout=10).text
