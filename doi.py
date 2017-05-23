#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to DOI inputs."""


from collections import defaultdict
from datetime import date as datetime_date
import re
from urllib.parse import unquote
import logging
from html import unescape

from requests import get as requests_get

from commons import Response, dictionary_to_response, detect_language, Name
from config import lang


# The regex is from:
# http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
DOI_SEARCH = re.compile(
    r'\b(10\.[0-9]{4,}(?:\.[0-9]+)*/(?:(?!["&\'])\S)+)\b'
).search
# Includes ShortDOIs (See: http://shortdoi.org/) and
# https://www.crossref.org/display-guidelines/
DOI_URL_MATCH = re.compile(
    r'https?://(dx\.)?doi\.org/'
).match


def doi_response(doi_or_url, pure=False, date_format='%Y-%m-%d') -> Response:
    """Return the response namedtuple."""
    if pure:
        doi = doi_or_url
    else:
        # unescape '&amp;', '&lt;', and '&gt;' in doi_or_url
        # decode percent encodings
        decoded_url = unquote(unescape(doi_or_url))
        m = DOI_SEARCH(decoded_url)
        doi = m.group(1)
    dictionary = crossref(doi)
    dictionary['date_format'] = date_format
    if lang == 'fa':
        dictionary['language'], dictionary['error'] = \
            detect_language(dictionary['title'])
    return dictionary_to_response(dictionary)


def crossref(doi) -> defaultdict:
    """Get the crossref.org json data for the given DOI. Return parsed data."""
    # See https://github.com/CrossRef/rest-api-doc/blob/master/api_format.md
    # for documentation.
    # Force using the version 1 of the API to prevent breakage. See:
    # https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md#how-to-manage-api-versions
    j = requests_get('http://api.crossref.org/v1/works/' + doi).json()
    assert j['status'] == 'ok'
    d = defaultdict(
        lambda: None, {k.lower(): v for k, v in j['message'].items()})

    d['cite_type'] = d.pop('type')

    for field in ('title', 'container-title', 'issn', 'isbn'):
        value = d[field]
        if value:
            d[field] = value[0]

    date = d['issued']['date-parts'][0]
    date_len = len(date)
    if date_len == 3:
        d['date'] = datetime_date(*date)
    elif date_len == 2:
        d['year'], d['month'] = str(date[0]), str(date[1])
    else:
        year = date[0]
        # date can be of the form [None]
        if year:
            d['year'] = str(date[0])

    authors = d['author']
    if authors:
        d['authors'] = \
            [Name(name['given'], name['family']) for name in authors]

    editors = d['editor']
    if editors:
        d['editors'] = \
            [Name(name['given'], name['family']) for name in editors]

    translators = d['translator']
    if translators:
        d['translators'] = \
            [Name(name['given'], name['family']) for name in translators]

    page = d['page']
    if page:
        d['page'] = page.replace('-', '–')

    return d


logger = logging.getLogger(__name__)
