from typing import Optional

from lib.commons import request
from urllib.parse import quote_plus


def get_citoid_dict(query: str, quote=False, /) -> Optional[dict]:
    if quote is True:
        query = quote_plus(query)
    # https://www.mediawiki.org/wiki/Citoid/API
    r = request(
        'https://en.wikipedia.org/api/rest_v1/data/citation/mediawiki/' + query
    )
    r.raise_for_status()

    j0 = r.json()[0]
    get = j0.get

    d = {}

    cite_type = d['cite_type'] = j0['itemType']
    # worldcat url is not needed since OCLC param will create it
    # d['url'] = j0['url']
    if (oclc := get('oclc')) is not None:
        d['oclc'] = oclc
    d['title'] = j0['title']

    authors = get('author')
    contributors = get('contributor')

    if authors is not None and contributors is not None:
        d['authors'] = authors + contributors
    elif authors is not None:
        d['authors'] = authors
    elif contributors is not None:
        d['authors'] = contributors

    if (publisher := get('publisher')) is not None:
        d['publisher'] = publisher
    elif (publisher := get('university')) is not None:
        d['publisher'] = publisher

    if (degree := get('thesisType')) is not None:
        d['thesisType'] = degree

    if (place := get('place')) is not None:
        d['publisher-location'] = place

    if (place := get('DOI')) is not None:
        d['doi'] = place

    if (date := get('date')) is not None:
        d['date'] = date

    return d
