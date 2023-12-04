from typing import Optional

from lib.commons import request
from urllib.parse import quote_plus

TRANSLATE = {
    'thesisType': 'thesisType',
    'place': 'publisher-location',
    'DOI': 'doi',
    'issue': 'issue',
    'language': 'language',
    'pages': 'pages',
    # 'url': 'url',
    'volume': 'volume',
    'itemType': 'cite_type',
}


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

    if cite_type == 'journalArticle':
        if (journal := get('publicationTitle')) is not None:
            d['journal'] = journal

    if (issn := get('ISSN')) is not None:
        d['issn'] = issn[0]

    if (date := get('date')) is not None:
        splits = date.split('-')
        if len(splits) == 2:  # YYYY-MM
            d['date'] = splits[0]
        else:
            d['date'] = date

    for citoid_key, citer_key in TRANSLATE.items():
        if (value := get(citoid_key)) is not None:
            d[citer_key] = value

    return d
