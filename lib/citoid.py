from functools import partial
from urllib.parse import quote_plus

from regex import compile as rc

from lib import four_digit_num, request
from lib.commons import find_any_date

TRANSLATE = {
    # 'url': 'url',
    'DOI': 'doi',
    'issue': 'issue',
    'itemType': 'cite_type',
    'language': 'language',
    'oclc': 'oclc',
    'pages': 'page',
    'place': 'publisher-location',
    'thesisType': 'thesisType',
    'title': 'title',
    'volume': 'volume',
    'PMID': 'pmid',
    'PMCID': 'pmcid',
}

rm_non_numeric = partial(rc(r'\D').sub, '')


def citoid_data(query: str, quote=False, /) -> dict:
    if quote is True:
        query = quote_plus(query)
    # https://www.mediawiki.org/wiki/Citoid/API
    r = request(
        'https://en.wikipedia.org/api/rest_v1/data/citation/mediawiki/' + query
    )

    j0 = r.json()[0]
    get = j0.get

    d = {}

    for citoid_key, citer_key in TRANSLATE.items():
        if (value := get(citoid_key)) is not None:
            d[citer_key] = value

    if (oclc := d.get('oclc')) is not None:
        d['oclc'] = rm_non_numeric(oclc)

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

    if (cite_type := d['cite_type']) == 'journalArticle':
        d['cite_type'] = 'journal'
        if (journal := get('publicationTitle')) is not None:
            d['journal'] = journal
    elif cite_type == 'bookSection':
        d['cite_type'] = 'book'
        if (book := get('bookTitle')) is not None:
            d['chapter'] = j0['title']
            d['title'] = book
    elif cite_type == 'conferencePaper':
        d['cite_type'] = 'conference'
        if (title := get('proceedingsTitle')) is not None:
            d['title'] = title
    elif cite_type == 'webpage':
        d['cite_type'] = 'web'
        if (website := get('websiteTitle')) is not None:
            d['website'] = website

    if (issn := get('ISSN')) is not None:
        d['issn'] = issn[0]

    if (isbn := get('ISBN')) is not None:
        d['isbn'] = isbn[0]

    if (date := get('date')) is not None:
        if (found_date := find_any_date(date)) is None:
            # e.g. date == "Nov.-Dec./1999"
            if (m := four_digit_num(date)) is not None:
                d['date'] = m[0]
        else:
            d['date'] = found_date

    return d
