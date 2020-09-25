"""Codes related to DOI inputs."""


from collections import defaultdict
from datetime import date as datetime_date
from urllib.parse import unquote
from html import unescape

from langid import classify
from regex import compile as regex_compile, VERBOSE

from lib.commons import dict_to_sfn_cit_ref, request
from config import LANG


# The regex is from:
# http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
DOI_SEARCH = regex_compile(
    r'''
    \b(
        10\.[0-9]{4,}+
        (?:\.[0-9]++)*+
        /[^"&\'\s]++
    )\b
    ''',
    VERBOSE,
).search


def doi_scr(doi_or_url, pure=False, date_format='%Y-%m-%d') -> tuple:
    """Return the response namedtuple."""
    if pure:
        doi = doi_or_url
    else:
        # unescape '&amp;', '&lt;', and '&gt;' in doi_or_url
        # decode percent encodings
        decoded_url = unquote(unescape(doi_or_url))
        doi = DOI_SEARCH(decoded_url)[1]
    dictionary = get_crossref_dict(doi)
    dictionary['date_format'] = date_format
    if LANG == 'fa':
        dictionary['language'] = classify(dictionary['title'])[0]
    return dict_to_sfn_cit_ref(dictionary)


def get_crossref_dict(doi) -> defaultdict:
    """Return the parsed data of crossref.org for the given DOI."""
    # See https://github.com/CrossRef/rest-api-doc/blob/master/api_format.md
    # for documentation.
    # Force using the version 1 of the API to prevent breakage. See:
    # https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md#how-to-manage-api-versions
    j = request('http://api.crossref.org/v1/works/' + doi).json()
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
        # https://github.com/CrossRef/rest-api-doc/issues/169
        if year:
            d['year'] = str(date[0])

    extract_names(d, 'author', 'authors')
    extract_names(d, 'editor', 'editors')
    extract_names(d, 'translator', 'translators')

    page = d['page']
    if page:
        d['page'] = page.replace('-', '–')

    return d


def extract_names(d: dict, from_key: str, to_key: str):
    from_values = d[from_key]
    if from_values is None:
        return
    to_values = d[to_key] = []
    authors_append = to_values.append
    for from_value in from_values:
        try:
            authors_append((from_value['given'], from_value['family']))
        except KeyError:
            pass
