"""Codes required to create citation templates for wikifa."""


from collections import defaultdict
from datetime import date
from logging import getLogger
from random import seed as randseed, choice as randchoice
from string import digits, ascii_lowercase

from lib.generator_en import (
    DOI_URL_MATCH, sfn_cit_ref as en_citations, fullname)
from lib.language import TO_TWO_LETTER_CODE


TYPE_TO_CITE = {
    # BibTex types. Descriptions are from
    # http://ctan.um.ac.ir/biblio/bibtex/base/btxdoc.pdf
    # A part of a book, which may be a chapter (or section or whatever) and/or
    # a range of pages.
    'inbook': 'کتاب',
    # A work that is printed and bound, but without a named publisher or
    # sponsoring institution.
    # Note: Yadkard does not currently support the `howpublished` option.
    'booklet': 'کتاب',
    # A part of a book having its own title.
    'incollection': 'کتاب',
    # Technical documentation.
    # Template:Cite manual is a redirect to Template:Cite_book on enwiki.
    'manual': 'کتاب',
    # An article from a journal or magazine.
    'article': 'ژورنال',
    # The same as INPROCEEDINGS, included for Scribe compatibility.
    'conference': 'conference',
    # An article in a conference proceedings.
    'inproceedings': 'conference',
    # A Master's thesis.
    'mastersthesis': 'thesis',
    # A PhD thesis.
    'phdthesis': 'thesis',
    # A report published by a school or other institution, usually numbered
    # within a series.
    'techreport': 'techreport',
    # Use this type when nothing else fits.
    'misc': '',
    # Types used by Yadkard.
    'web': 'وب',
    # crossref types (https://api.crossref.org/v1/types)
    'book-section': 'کتاب',
    'monograph': 'کتاب',
    'report': 'report',
    'book-track': 'کتاب',
    'journal-article': 'ژورنال',
    'book-part': 'کتاب',
    'other': '',
    'book': 'کتاب',
    'journal-volume': 'ژورنال',
    'book-set': 'کتاب',
    'reference-entry': '',
    'proceedings-article': 'conference',
    'journal': 'ژورنال',
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=22368089&retmode=json&tool=my_tool&email=my_email@example.com
    'Journal Article': 'ژورنال',
    'component': '',
    'book-chapter': 'کتاب',
    'report-series': 'report',
    'proceedings': 'conference',
    'standard': '',
    'reference-book': 'کتاب',
    'posted-content': '',
    'journal-issue': 'ژورنال',
    'dissertation': 'thesis',
    'dataset': '',
    'book-series': 'کتاب',
    'edited-book': 'کتاب',
    'standard-series': '',
    'jour': 'ژورنال',
}.get

# According to https://en.wikipedia.org/wiki/Help:Footnotes,
# the characters '!$%&()*,-.:;<@[]^_`{|}~' are also supported. But they are
# hard to use.
LOWER_ALPHA_DIGITS = digits + ascii_lowercase

DIGITS_TO_FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def sfn_cit_ref(d: defaultdict) -> tuple:
    """Return sfn, citation, and ref."""
    cite_type = TYPE_TO_CITE(d['cite_type'])
    if not cite_type:
        logger.warning('Unknown citation type: %s, d: %s', cite_type, d)
        cite_type = ''
    if cite_type in ('کتاب', 'ژورنال', 'وب'):
        cit = '* {{یادکرد ' + cite_type
    else:
        return en_citations(d)

    authors = d['authors']
    if authors:
        cit += names2para(authors, 'نام', 'نام خانوادگی', 'نویسنده')
        sfn = '&lt;ref&gt;{{پک'
        for first, last in authors[:4]:
            sfn += ' | ' + last
    else:
        sfn = '&lt;ref&gt;{{پک/بن'

    editors = d['editors']
    if editors:
        cit += names2para(
            editors, 'نام ویراستار', 'نام خانوادگی ویراستار', 'ویراستار')

    translators = d['translators']
    if translators:
        cit += names1para(translators, 'ترجمه')

    others = d['others']
    if others:
        cit += names1para(others, 'دیگران')

    year = d['year']
    if year:
        sfn += ' | ' + year

    if cite_type == 'book':
        booktitle = d['booktitle'] or d['container-title']
    else:
        booktitle = None

    title = d['title']
    if booktitle:
        cit += ' | عنوان=' + booktitle
        if title:
            cit += ' | فصل=' + title
    elif title:
        cit += ' | عنوان=' + title
        sfn += ' | ک=' + d['title']

    if cite_type == 'ژورنال':
        journal = d['journal'] or d['container-title']
    else:
        journal = d['journal']

    if journal:
        cit += ' | ژورنال=' + journal
    else:
        website = d['website']
        if website:
            cit += ' | وبگاه=' + website

    chapter = d['chapter']
    if chapter:
        cit += ' | فصل=' + chapter

    publisher = d['publisher'] or d['organization']
    if publisher:
        cit += ' | ناشر=' + publisher

    address = d['address'] or d['publisher-location']
    if address:
        cit += ' | مکان=' + address

    edition = d['edition']
    if edition:
        cit += ' | ویرایش=' + edition

    series = d['series']
    if series:
        cit += ' | سری=' + series

    volume = d['volume']
    if volume:
        cit += ' | جلد=' + volume

    issue = d['issue'] or d['number']
    if issue:
        cit += ' | شماره=' + issue

    ddate = d['date']
    if ddate:
        if isinstance(ddate, str):
            cit += ' | تاریخ=' + ddate
        else:
            cit += ' | تاریخ=' + date.isoformat(ddate)
    elif year:
        cit += ' | سال=' + year

    isbn = d['isbn']
    if isbn:
        cit += ' | شابک=' + isbn

    issn = d['issn']
    if issn:
        cit += ' | issn=' + issn

    pmid = d['pmid']
    if pmid:
        cit += ' | pmid=' + pmid

    pmcid = d['pmcid']
    if pmcid:
        cit += ' | pmc=' + pmcid

    doi = d['doi']
    if doi:
        cit += ' | doi=' + doi

    oclc = d['oclc']
    if oclc:
        cit += ' | oclc=' + oclc

    jstor = d['jstor']
    if jstor:
        cit += f' | jstor={jstor}'
        jstor_access = d['jstor-access']
        if jstor_access:
            cit += f' | jstor-access=free'

    pages = d['page']
    if cite_type == 'ژورنال':
        if pages:
            cit += ' | صفحه=' + pages

    url = d['url']
    if url:
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not DOI_URL_MATCH(url):
            cit += ' | پیوند=' + url
        else:
            # To prevent addition of access date
            url = None

    archive_url = d['archive-url']
    if archive_url:
        cit += (
            f' | پیوند بایگانی={archive_url}'
            f' | تاریخ بایگانی={d["archive-date"].isoformat()}'
            f" | پیوند مرده={('آری' if d['url-status'] == 'yes' else 'نه')}")

    language = d['language']
    if language:
        language = TO_TWO_LETTER_CODE(language.lower(), language)
        if cite_type == 'وب':
            cit += f' | کد زبان={language}'
        else:
            cit += f' | زبان={language}'
        sfn += f' | زبان={language}'

    if pages:
        sfn += f' | ص={pages}'
    # Seed the random generator before adding today's date.
    randseed(cit)
    ref_name = (
        randchoice(ascii_lowercase)  # it should contain at least one non-digit
        + ''.join(randchoice(LOWER_ALPHA_DIGITS) for _ in range(4)))
    if url:
        cit += f' | تاریخ بازبینی={date.today().isoformat()}'

    if not pages and cite_type != 'وب':
        sfn += ' | ص='

    cit += '}}'
    sfn += '}}\u200F&lt;/ref&gt;'
    # Finally create the ref tag.
    ref = cit[2:]
    if pages and ' | صفحه=' not in ref:
        ref = f'{ref[:-2]} | صفحه={pages}}}}}'
    elif not url:
        ref = f'{ref[:-2]} | صفحه=}}}}'
    ref = f'&lt;ref name="{ref_name}"&gt;{ref}\u200F&lt;/ref&gt;'
    return sfn, cit, ref


def names2para(names, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    c = 0
    s = ''
    for first, last in names:
        c += 1
        if c == 1:
            if first or not nofn_parameter:
                s += (
                    f' | {ln_parameter}=' + last +
                    f' | {fn_parameter}=' + first)
            else:
                s += f' | {nofn_parameter}=' + fullname(first, last)
        else:
            if first or not nofn_parameter:
                s += (
                    f' | {ln_parameter}{str(c).translate(DIGITS_TO_FA)}'
                    f'={last} | {fn_parameter}{str(c).translate(DIGITS_TO_FA)}'
                    f'={first}')
            else:
                s += (
                    f' | {nofn_parameter}{str(c).translate(DIGITS_TO_FA)}'
                    f'={fullname(first, last)}')
    return s


def names1para(translators, para):
    """Take list of names. Return the string to be appended to citation."""
    s = f' | {para}='
    c = 0
    for first, last in translators:
        c += 1
        if c == 1:
            s += fullname(first, last)
        elif c == len(translators):
            s += f' و {fullname(first, last)}'
        else:
            s += f'، {fullname(first, last)}'
    return s


logger = getLogger(__name__)
