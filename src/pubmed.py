#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes specifically related to PubMed inputs."""

from collections import defaultdict
from config import ncbi_api_key, ncbi_email, ncbi_tool
from datetime import datetime
import logging
from re import compile as re_compile
from threading import Thread

from requests import get as requests_get

from src.commons import Response, dictionary_to_response, Name, b_TO_NUM
from src.doi import crossref

NON_DIGITS_SUB = re_compile(r'[^\d]').sub

NCBI_URL = (
    'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'
    f'api_key={ncbi_api_key}&retmode=json&tool={ncbi_tool}&email={ncbi_email}'
)
PUBMED_URL = NCBI_URL + '&db=pubmed&id='
PMC_URL = NCBI_URL + '&db=pmc&id='


def pmid_response(pmid: str, date_format='%Y-%m-%d') -> Response:
    """Return the response namedtuple."""
    pmid = NON_DIGITS_SUB('', pmid)
    dictionary = ncbi('pmid', pmid)
    dictionary['date_format'] = date_format
    return dictionary_to_response(dictionary)


def pmcid_response(pmcid: str, date_format='%Y-%m-%d') -> Response:
    """Return the response namedtuple."""
    pmcid = NON_DIGITS_SUB('', pmcid)
    dictionary = ncbi('pmcid', pmcid)
    dictionary['date_format'] = date_format
    return dictionary_to_response(dictionary)


def ncbi(type_: str, id_: str) -> defaultdict:
    """Return the NCBI data for the given id_."""
    # According to https://www.ncbi.nlm.nih.gov/pmc/tools/get-metadata/
    if type_ == 'pmid':
        result_get = requests_get(
            PUBMED_URL + id_,
            timeout=10,
        ).json()['result'][id_].get
    else:  # type_ == 'pmcid'
        result_get = requests_get(
            PMC_URL + id_,
            timeout=10,
        ).json()['result'][id_].get

    d = defaultdict(lambda: None)

    doi = None
    articleids = result_get('articleids', ())
    for articleid in articleids:
        idtype = articleid['idtype']
        if idtype == 'doi':
            doi = articleid['value']
            crossref_dict = {}
            crossref_thread = Thread(
                target=crossref_update, args=(crossref_dict, doi)
            )
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
    date_len = len(date_split)
    if date_len == 3:
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
        authors_append(Name(first, last))
    d['authors'] = authors

    d['journal'] = result_get('fulljournalname') or result_get('source')

    for field in ('title', 'volume', 'issue'):
        d[field] = result_get(field)

    d['page'] = result_get('pages', '').replace('-', '–')

    lang = result_get('lang')
    if lang:
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
        dct.update(crossref(doi))
    except Exception:
        logger.exception(
            f'There was an error in resolving crossref DOI: {doi}'
        )


logger = logging.getLogger(__name__)
