#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes required to create citation templates for wikifa."""


from collections import defaultdict
from datetime import date
from logging import getLogger
from random import seed as randseed, choice as randchoice
from string import digits, ascii_lowercase

from src.generator_en import citations as en_citations, DOI_URL_MATCH
from src.language import TO_TWO_LETTER_CODE


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
}.get

# According to https://en.wikipedia.org/wiki/Help:Footnotes,
# the characters '!$%&()*,-.:;<@[]^_`{|}~' are also supported. But they are
# hard to use.
LOWER_ALPHA_DIGITS = digits + ascii_lowercase

DIGITS_TO_FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

def citations(d: defaultdict) -> tuple:
    """Create citation templates using the given dictionary."""
    cite_type = TYPE_TO_CITE(d['cite_type'])
    if not cite_type:
        logger.warning(f'Unknown citation type: {cite_type}, d: {d}')
        cite_type = ''
    if cite_type in ('کتاب', 'ژورنال', 'وب'):
        cite = '* {{یادکرد ' + cite_type
    else:
        return en_citations(d)

    authors = d['authors']
    if authors:
        cite += names2para(authors, 'نام', 'نام خانوادگی', 'نویسنده')
        sfn = '&lt;ref&gt;{{پک'
        for author in authors[:4]:
            sfn += ' | ' + author.lastname
    else:
        sfn = '&lt;ref&gt;{{پک/بن'

    editors = d['editors']
    if editors:
        cite += names2para(
            editors, 'نام ویراستار', 'نام خانوادگی ویراستار', 'ویراستار'
        )

    translators = d['translators']
    if translators:
        cite += names1para(translators, 'ترجمه')

    others = d['others']
    if others:
        cite += names1para(others, 'دیگران')

    year = d['year']
    if year:
        sfn += ' | ' + year

    if cite_type == 'book':
        booktitle = d['booktitle'] or d['container-title']
    else:
        booktitle = None

    title = d['title']
    if booktitle:
        cite += ' | عنوان=' + booktitle
        if title:
            cite += ' | فصل=' + title
    elif title:
        cite += ' | عنوان=' + title
        sfn += ' | ک=' + d['title']

    if cite_type == 'ژورنال':
        journal = d['journal'] or d['container-title']
    else:
        journal = d['journal']

    if journal:
        cite += ' | ژورنال=' + journal
    else:
        website = d['website']
        if website:
            cite += ' | وب‌گاه=' + website

    chapter = d['chapter']
    if chapter:
        cite += ' | فصل=' + chapter

    publisher = d['publisher'] or d['organization']
    if publisher:
        cite += ' | ناشر=' + publisher

    address = d['address'] or d['publisher-location']
    if address:
        cite += ' | مکان=' + address

    edition = d['edition']
    if edition:
        cite += ' | ویرایش=' + edition

    series = d['series']
    if series:
        cite += ' | سری=' + series

    volume = d['volume']
    if volume:
        cite += ' | جلد=' + volume

    issue = d['issue'] or d['number']
    if issue:
        cite += ' | شماره=' + issue

    ddate = d['date']
    if ddate:
        if isinstance(ddate, str):
            cite += ' | تاریخ=' + ddate
        else:
            cite += ' | تاریخ=' + date.isoformat(ddate)

    if year:
        cite += ' | سال=' + year

    month = d['month']
    if month:
        cite += ' | ماه=' + month

    isbn = d['isbn']
    if isbn:
        cite += ' | شابک=' + isbn

    issn = d['issn']
    if issn:
        cite += ' | issn=' + issn

    pmid = d['pmid']
    if pmid:
        cite += ' | pmid=' + pmid

    pmcid = d['pmcid']
    if pmcid:
        cite += ' | pmc=' + pmcid

    doi = d['doi']
    if doi:
        cite += ' | doi=' + doi

    pages = d['page']
    if cite_type == 'ژورنال':
        if pages:
            cite += ' | صفحه=' + pages

    url = d['url']
    if url:
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not DOI_URL_MATCH(url):
            cite += ' | پیوند=' + url
        else:
            # To prevent addition of access date
            url = None

    archive_url = d['archive-url']
    if archive_url:
        cite += (
            ' | پیوند بایگانی=' + archive_url +
            ' | تاریخ بایگانی=' + d['archive-date'].isoformat() +
            ' | پیوند مرده=' + ('آری' if d['dead-url'] == 'yes' else 'نه')
        )

    language = d['language']
    if language:
        language = TO_TWO_LETTER_CODE(language.lower(), language)
        if cite_type == 'وب':
            cite += ' | کد زبان=' + language
        else:
            cite += ' | زبان=' + language
        sfn += ' | زبان=' + language

    if pages:
        sfn += ' | ص=' + pages
    # Seed the random generator before adding today's date.
    randseed(cite)
    ref_name = (
        randchoice(ascii_lowercase)  # it should contain at least one non-digit
        + ''.join(randchoice(LOWER_ALPHA_DIGITS) for _ in range(4))
    )
    if url:
        cite += ' | تاریخ بازبینی=' + date.today().isoformat()

    if not pages and cite_type != 'وب':
        sfn += ' | ص='

    cite += '}}'
    sfn += '}}\u200F&lt;/ref&gt;'
    # Finally create the ref tag.
    ref = cite[2:]
    if pages and ' | صفحه=' not in ref:
        ref = ref[:-2] + ' | صفحه=' + pages + '}}'
    elif not url:
        ref = ref[:-2] + ' | صفحه=}}'
    ref = '&lt;ref name="' + ref_name + '"&gt;' + ref + '\u200F&lt;/ref&gt;'
    return cite, sfn, ref


def names2para(names, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    c = 0
    s = ''
    for name in names:
        c += 1
        if c == 1:
            if name.firstname or not nofn_parameter:
                s += (
                    ' | ' + ln_parameter + '=' + name.lastname +
                    ' | ' + fn_parameter + '=' + name.firstname
                )
            else:
                s += ' | ' + nofn_parameter + '=' + name.fullname
        else:
            if name.firstname or not nofn_parameter:
                s += (
                    ' | ' + ln_parameter + str(c).translate(DIGITS_TO_FA)
                    + '=' + name.lastname +
                    ' | ' + fn_parameter + str(c).translate(DIGITS_TO_FA)
                    + '=' + name.firstname
                )
            else:
                s += (
                    ' | ' + nofn_parameter + str(c).translate(DIGITS_TO_FA)
                    + '=' + name.fullname
                )
    return s


def names1para(translators, para):
    """Take list of names. Return the string to be appended to citation."""
    s = ' | ' + para + '='
    c = 0
    for name in translators:
        c += 1
        if c == 1:
            s += name.fullname
        elif c == len(translators):
            s += ' و ' + name.fullname
        else:
            s += '، ' + name.fullname
    return s


logger = getLogger(__name__)
