"""Codes specifically related to PubMed inputs."""

from collections import defaultdict
from typing import Any

from config import NCBI_API_KEY, NCBI_EMAIL, NCBI_TOOL
from datetime import datetime
from logging import getLogger
from threading import Thread

from regex import compile as regex_compile

from lib.commons import b_TO_NUM, request
from lib.doi import get_crossref_dict

NON_DIGITS_SUB = regex_compile(r'[^\d]').sub

NCBI_URL = (
    'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'
    'api_key=' + NCBI_API_KEY + '&retmode=json&tool=' + NCBI_TOOL + '&email='
    + NCBI_EMAIL)
PUBMED_URL = NCBI_URL + '&db=pubmed&id='
PMC_URL = NCBI_URL + '&db=pmc&id='


class NCBIError(Exception):

    pass


def pmid_dict(pmid: str, date_format='%Y-%m-%d', /) -> dict:
    """Return the response namedtuple."""
    pmid = NON_DIGITS_SUB('', pmid)
    dictionary = ncbi('pmid', pmid)
    dictionary['date_format'] = date_format
    return dictionary


def pmcid_dict(pmcid: str, date_format='%Y-%m-%d', /) -> dict:
    """Return the response namedtuple."""
    pmcid = NON_DIGITS_SUB('', pmcid)
    dictionary = ncbi('pmcid', pmcid)
    dictionary['date_format'] = date_format
    return dictionary


def ncbi(type_: str, id_: str) -> defaultdict:
    """Return the NCBI data for the given id_."""
    # According to https://www.ncbi.nlm.nih.gov/pmc/tools/get-metadata/
    if type_ == 'pmid':
        json_response = request(PUBMED_URL + id_).json()
    else:  # type_ == 'pmcid'
        json_response = request(PMC_URL + id_).json()
    if 'error' in json_response:
        # Example error message if rates are exceeded:
        # {"error":"API rate limit exceeded","count":"11"}
        # https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Coming_in_May_2018_API_Keys
        # Return a 503 Service Unavailable
        raise NCBIError(json_response)
    result_get = json_response['result'][id_].get
    d : defaultdict[str, Any] = defaultdict(lambda: None)

    doi = None
    articleids = result_get('articleids', ())
    for articleid in articleids:
        if (idtype := articleid['idtype']) == 'doi':
            doi = articleid['value']
            crossref_dict = {}
            crossref_thread = Thread(
                target=crossref_update, args=(crossref_dict, doi))
            crossref_thread.start()
            d['doi'] = doi
        elif idtype == 'pmcid':
            # Use NON_DIGITS_SUB to remove the PMC prefix e.g. in PMC3539452
            d['pmcid'] = NON_DIGITS_SUB('', articleid['value'])
        elif idtype == 'pubmed':
            d['pmid'] = articleid['value']
        else:
            d[idtype] = articleid['value']

    d['issn'] = result_get('issn') or result_get('essn')  # essn is eissn

    d['cite_type'] = result_get('pubtype', ('journal',))[0]

    d['booktitle'] = result_get('booktitle') or result_get('bookname')
    d['edition'] = result_get('edition')
    d['publisher-location'] = result_get('publisherlocation')
    d['publisher'] = result_get('publishername')
    d['url'] = result_get('availablefromurl')
    d['chapter'] = result_get('chapter')

    date = result_get('pubdate') or result_get('epubdate') \
        or result_get('printpubdate')
    date_split = date.split(' ')
    if (date_len := len(date_split)) == 3:
        d['date'] = datetime.strptime(date, '%Y %b %d')
    elif date_len == 2:
        d['year'], d['month'] = \
            date_split[0], str(b_TO_NUM[date_split[1].lower()])
    else:
        d['year'] = date

    authors = []
    authors_append = authors.append
    for author in result_get('authors', ()):
        if author['authtype'] != 'Author':
            continue
        parts = author['name'].split()
        for i, p in enumerate(parts):
            if p.isupper():
                last = ' '.join(parts[:i])
                first = ' '.join(parts[i:])
                break
        else:
            last = ' '.join(parts[:-1])
            first = parts[-1]
        authors_append((first, last))
    d['authors'] = authors

    d['journal'] = result_get('fulljournalname') or result_get('source')

    for field in ('title', 'volume', 'issue'):
        d[field] = result_get(field)

    d['page'] = result_get('pages', '').replace('-', '–')

    if (lang := result_get('lang')) is not None:
        d['language'] = lang[0]

    if doi:
        # noinspection PyUnboundLocalVariable
        crossref_thread.join()
        # noinspection PyUnboundLocalVariable
        d.update(crossref_dict)

    return d


def crossref_update(dct: dict, doi: str):
    """Update dct using crossref result."""
    # noinspection PyBroadException
    try:
        dct.update(get_crossref_dict(doi))
    except Exception:
        logger.exception(
            'There was an error in resolving crossref DOI: ' + doi)


logger = getLogger(__name__)
