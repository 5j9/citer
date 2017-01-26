#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to Noormags website."""

import re
from threading import Thread

from requests import get as requests_get

from commons import dictionary_to_response, Response
from bibtex import parse as bibtex_parse
from ris import parse as ris_parse


def noormags_response(url: str, date_format: str= '%Y-%m-%d') -> Response:
    """Create the response namedtuple."""
    ris_collection = {}
    ris_thread = Thread(target=ris_fetcher_thread, args=(url, ris_collection))
    ris_thread.start()
    dictionary = bibtex_parse(get_bibtex(url))
    dictionary['date_format'] = date_format
    # language parameter needs to be taken from RIS
    # other information are more accurate in bibtex
    # for example: http://www.noormags.com/view/fa/articlepage/104040
    # "IS  - 1" is wrong in RIS but "number = { 45 }," is correct in bibtex
    ris_thread.join()
    dictionary.update(ris_collection)
    return dictionary_to_response(dictionary)


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


def ris_fetcher_thread(url, ris_collection):
    """Fill the ris_dict. This function is called in a thread."""
    ris_dict = ris_parse(get_ris(url))
    language = ris_dict.get('language')
    if language:
        ris_collection['language'] = language
    authors = ris_dict.get('authors')
    if authors:
        ris_collection['authors'] = authors

