from collections.abc import Callable
from contextlib import AbstractContextManager, contextmanager
from functools import partial
from logging import INFO, Formatter, basicConfig, getLogger
from logging.handlers import RotatingFileHandler
from os.path import abspath, dirname
from random import choice, choices, seed
from ssl import CERT_NONE, create_default_context
from string import ascii_lowercase, digits
from typing import Literal, overload

from curl_cffi.requests import Response, Session
from regex import compile as rc

from config import USER_AGENT


def get_logger():
    basicConfig(
        format='%(pathname)s:%(lineno)d\n%(asctime)s %(levelname)s %(message)s'
    )
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    src_dir = dirname(abspath(__file__))
    handler = RotatingFileHandler(
        filename=f'{src_dir}/citer.log',
        mode='a',
        maxBytes=20000,
        backupCount=0,
        encoding='utf-8',
    )
    handler.setLevel(INFO)
    handler.setFormatter(
        Formatter('\n%(asctime)s\n%(levelname)s\n%(message)s\n')
    )
    logger.addHandler(handler)
    return logger


logger = get_logger()


AGENT_HEADER = {
    'User-Agent': USER_AGENT,
}

context = create_default_context()
context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
context.check_hostname = False
context.verify_mode = CERT_NONE


def new_session() -> Session:
    return Session(verify=context, timeout=10.0, impersonate='chrome')  # type: ignore


session_usage = 0
session = new_session()


def mortal_session() -> Session:
    global session, session_usage
    if session_usage > 1000:  # to save memory by discarding unneeded cookies
        session_usage = 0
        session = new_session()
        return session
    session_usage += 1
    return session


Method = Literal['GET'] | Literal['POST'] | Literal['HEAD']


@overload
def request(
    url,
    *,
    spoof=False,
    method: Method = 'GET',
    stream: Literal[True],
    **kwargs,
) -> AbstractContextManager[Response]: ...
@overload
def request(
    url,
    *,
    spoof=False,
    method: Method = 'GET',
    stream: Literal[False] = False,
    **kwargs,
) -> Response: ...


@contextmanager
def enhanced_stream_ctx(ctx: AbstractContextManager[Response]):
    with ctx as response:
        response.raise_for_status()
        yield response


def request(
    url,
    *,
    spoof=False,
    method: Method = 'GET',
    stream=False,
    **kwargs,
) -> Response | AbstractContextManager[Response]:
    headers = None if spoof is True else AGENT_HEADER
    if (kw_headers := kwargs.pop('headers', None)) is not None:
        if headers is not None:
            headers |= kw_headers
        else:
            headers = kw_headers
    if stream is True:
        ctx = mortal_session().stream(method, url, headers=headers, **kwargs)
        return enhanced_stream_ctx(ctx)

    r = mortal_session().request(method, url, headers=headers, **kwargs)
    r.raise_for_status()
    return r


rc = partial(rc, cache_pattern=False)

four_digit_num = rc(r'\d\d\d\d').search


def fullname(first: str, last: str) -> str:
    if first:
        return f'{first} {last}'
    return last


# Includes ShortDOIs (See: http://shortdoi.org/) and
# https://www.crossref.org/display-guidelines/
doi_url_match = rc(r'https?://(dx\.)?doi\.org/').match

known_free_doi_registrants = {
    '1100',
    '1155',
    '1186',
    '1371',
    '1629',
    '1989',
    '1999',
    '2147',
    '2196',
    '3285',
    '3389',
    '3390',
    '3410',
    '3748',
    '3814',
    '3847',
    '3897',
    '4061',
    '4089',
    '4103',
    '4172',
    '4175',
    '4236',
    '4239',
    '4240',
    '4251',
    '4252',
    '4253',
    '4254',
    '4291',
    '4292',
    '4329',
    '4330',
    '4331',
    '5194',
    '5306',
    '5312',
    '5313',
    '5314',
    '5315',
    '5316',
    '5317',
    '5318',
    '5319',
    '5320',
    '5321',
    '5334',
    '5402',
    '5409',
    '5410',
    '5411',
    '5412',
    '5492',
    '5493',
    '5494',
    '5495',
    '5496',
    '5497',
    '5498',
    '5499',
    '5500',
    '5501',
    '5527',
    '5528',
    '5662',
    '6064',
    '6219',
    '7167',
    '7217',
    '7287',
    '7482',
    '7490',
    '7554',
    '7717',
    '7766',
    '11131',
    '11569',
    '11647',
    '11648',
    '12688',
    '12703',
    '12715',
    '12998',
    '13105',
    '14293',
    '14303',
    '15215',
    '15412',
    '15560',
    '16995',
    '17645',
    '19080',
    '19173',
    '20944',
    '21037',
    '21468',
    '21767',
    '22261',
    '22459',
    '24105',
    '24196',
    '24966',
    '26775',
    '30845',
    '32545',
    '35711',
    '35712',
    '35713',
    '35995',
    '36648',
    '37126',
    '37532',
    '37871',
    '47128',
    '47622',
    '47959',
    '52437',
    '52975',
    '53288',
    '54081',
    '54947',
    '55667',
    '55914',
    '57009',
    '58647',
    '59081',
}

free_doi_fullmatch = rc(r'10\.([^/]+)/[^\s–]*?[^.,]').fullmatch


def open_access_url(doi: str) -> str | None:
    # The following pattern is equavalant of '^10%.([^/]+)/[^%s–]-[^%.,]$' in
    # https://en.wikipedia.org/wiki/Module:Citation/CS1/Identifiers .
    m = free_doi_fullmatch(doi)
    if m is not None:
        if m[1] in known_free_doi_registrants:
            return ''

    try:
        oa = request(f'https://api.openaccessbutton.org/find?id={doi}').json()
    except Exception:
        logger.exception('Failed checking OA for doi: %s', doi)
        return None
    else:
        return oa.get('url')


type_to_cite = {
    # BibTex types. Descriptions are from
    # http://ctan.um.ac.ir/biblio/bibtex/base/btxdoc.pdf
    # A part of a book, which may be a chapter (or section or whatever) and/or
    # a range of pages.
    'inbook': 'book',
    # A work that is printed and bound, but without a named publisher or
    # sponsoring institution.
    # Note: Yadkard does not currently support the `howpublished` option.
    'booklet': 'book',
    # A part of a book having its own title.
    'incollection': 'book',
    # Technical documentation.
    # Template:Cite manual is a redirect to Template:Cite_book on enwiki.
    'manual': 'book',
    # An article from a journal or magazine.
    'article': 'journal',
    'article-journal': 'journal',
    # The same as INPROCEEDINGS, included for Scribe compatibility.
    'conference': 'conference',
    # An article in a conference proceedings.
    'inproceedings': 'conference',
    # A Master's thesis.
    # todo: convert to degree/type parameter
    'mastersthesis': 'thesis',
    # A PhD thesis.
    'phdthesis': 'thesis',
    # A report published by a school or other institution, usually numbered
    # within a series.
    # Todo: Add support for Template:Cite techreport
    'techreport': 'techreport',
    # Use this type when nothing else fits.
    'misc': '',
    # Types used by Yadkard.
    'web': 'web',
    # crossref types (https://api.crossref.org/v1/types)
    'book-section': 'book',
    'monograph': 'book',
    'report': 'report',
    'book-track': 'book',
    'journal-article': 'journal',
    'book-part': 'book',
    'other': '',
    'book': 'book',
    'journal-volume': 'journal',
    'book-set': 'book',
    'reference-entry': '',
    'proceedings-article': 'conference',
    'journal': 'journal',
    'jour': 'journal',
    'jrnl': 'journal',
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=22368089&retmode=json&tool=my_tool&email=my_email@example.com
    'Journal Article': 'journal',
    'component': '',
    'book-chapter': 'book',
    'report-series': 'report',
    'proceedings': 'conference',
    'standard': '',
    'reference-book': 'book',
    'posted-content': '',
    'journal-issue': 'journal',
    'dissertation': 'thesis',
    'dataset': '',
    'book-series': 'book',
    'edited-book': 'book',
    'standard-series': '',
    'rprt': 'report',
    'thesis': 'thesis',
}.get


def make_ref_name(g: Callable) -> str:
    # A combination of possible `user_input`s is used as seed.
    seed(
        f'{g("url", "")}{g("isbn", "")}{g("doi", "")}'
        or g('oclc', '')
        or g('pmid', '')
        or g('pmcid', '')
    )
    return choice(
        ascii_lowercase
    ) + ''.join(  # it should contain at least one non-digit
        choices(digits, k=3)
    )
