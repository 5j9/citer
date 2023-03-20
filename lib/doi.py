"""Codes related to DOI inputs."""


from collections import defaultdict
from datetime import datetime
from html import unescape
from typing import Any
from urllib.parse import unquote_plus

from langid import classify

from config import LANG
from lib.commons import DOI_SEARCH, request


def doi_to_dict(doi_or_url, pure=False, date_format='%Y-%m-%d', /) -> dict:
    if pure:
        doi = doi_or_url
    else:
        # unescape '&amp;', '&lt;', and '&gt;' in doi_or_url
        # decode percent encodings
        decoded_url = unquote_plus(unescape(doi_or_url))
        doi = DOI_SEARCH(decoded_url)[0]
    dictionary = get_crossref_dict(doi)
    dictionary['date_format'] = date_format
    if LANG == 'fa':
        dictionary['language'] = classify(dictionary['title'])[0]
    return dictionary


def get_crossref_dict(doi) -> defaultdict:
    """Return the parsed data of crossref.org for the given DOI."""
    # See https://citation.crosscite.org/docs.html for documentation.
    j = request(
        f'https://doi.org/{doi}',
        headers={"Accept": "application/vnd.citationstyles.csl+json"}
    ).json()

    d : defaultdict[str, Any] = defaultdict(
        lambda: None, {k.lower(): v for k, v in j.items()})

    d['cite_type'] = d['type']

    if (author := d['author']) is not None:
        d['authors'] = [
            (a['given'], a['family']) for a in author if 'given' in a
        ]

    if (issn := d['issn']) is not None:
        d['issn'] = issn[0]

    if (published := d['published']) is not None:
        date = published['date-parts'][0]
        if len(date) == 3:
            d['date'] = datetime(*date)
        else:  # todo: better handle the case where len == 2
            d['year'] = f'{date[0]}'

    if (page := d['page']) is not None:
        d['page'] = page.replace('-', '–')

    if (isbn := d['isbn']) is not None:
        d['isbn'] = isbn[0]

    return d


def extract_names(d: dict, from_key: str, to_key: str):
    if (from_values := d[from_key]) is None:
        return
    to_values = d[to_key] = []
    authors_append = to_values.append
    for from_value in from_values:
        try:
            authors_append((from_value['given'], from_value['family']))
        except KeyError:
            pass
