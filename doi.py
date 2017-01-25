#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to DOI inputs."""


import re
from urllib.parse import unquote
import logging
from html import unescape

from requests import get as requests_get

from commons import Response, dictionary_to_response, detect_language
from config import lang
from bibtex import parse as bibtex_parse


# The regex is from:
# http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
DOI_SEARCH = re.compile(
    r'\b(10\.[0-9]{4,}(?:\.[0-9]+)*/(?:(?!["&\'])\S)+)\b'
).search


def doi_response(doi_or_url, pure=False, date_format='%Y-%m-%d') -> Response:
    """Create the response namedtuple."""
    if pure:
        doi = doi_or_url
    else:
        # unescape '&amp;', '&lt;', and '&gt;' in doi_or_url
        # decode percent encodings
        decoded_url = unquote(unescape(doi_or_url))
        m = DOI_SEARCH(decoded_url)
        if m:
            doi = m.group(1)
    url = 'http://dx.doi.org/' + doi
    bibtex = get_bibtex(url)
    if bibtex == 'Resource not found.':
        logger.info('DOI could not be resolved.\n' + url)
        return Response(
            error=100, sfnt='DOI could not be resolved.', ctnt=bibtex
        )
    else:
        dictionary = bibtex_parse(bibtex)
        dictionary['date_format'] = date_format
        if lang == 'fa':
            dictionary['language'], dictionary['error'] = \
                detect_language(dictionary['title'])
        return dictionary_to_response(dictionary)


def get_bibtex(doi_url):
    """Get BibTex file content from a DOI URL. Return as string."""
    return requests_get(
        doi_url, headers={'Accept': 'application/x-bibtex'}
    ).text

logger = logging.getLogger(__name__)

