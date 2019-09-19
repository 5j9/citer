#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes required to create English Wikipedia citation templates."""


from datetime import date as datetime_date
from functools import partial
from collections import defaultdict
from logging import getLogger

from regex import compile as regex_compile

from lib.language import TO_TWO_LETTER_CODE


# Includes ShortDOIs (See: http://shortdoi.org/) and
# https://www.crossref.org/display-guidelines/
DOI_URL_MATCH = regex_compile(r'https?://(dx\.)?doi\.org/').match
DIGITS_TO_EN = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')

refless = partial(regex_compile(
    r'( \| ref=({{.*?}}|harv))(?P<repl> \| |}})'
).sub, r'\g<repl>')

TYPE_TO_CITE = {
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
}.get


def sfn_cit_ref(d: defaultdict) -> tuple:
    """Create citation templates according to the given dictionary."""
    date_format = d['date_format']
    cite_type = TYPE_TO_CITE(d['cite_type'])
    if not cite_type:
        logger.warning('Unknown citation type: %s, d: %s', cite_type, d)
        cite_type = ''
    cit = '* {{cite ' + cite_type
    sfn = '{{sfn'

    authors = d['authors']
    publisher = d['publisher']
    website = d['website']
    title = d['title']

    if cite_type == 'journal':
        journal = d['journal'] or d['container-title']
    else:
        journal = d['journal']

    if authors:
        cit += names2para(authors, 'first', 'last', 'author')
        # {{sfn}} only supports a maximum of four authors
        for first, last in authors[:4]:
            sfn += ' | ' + last
    else:
        # the same order should be used in citation_template:
        sfn += ' | ' + (
            publisher or
            "''" + journal + "''" if journal else
            "''" + website + "''" if website else
            title or 'Anon.'
        )

    editors = d['editors']
    if editors:
        cit += names2para(editors, 'editor-first', 'editor-last', 'editor')
    translators = d['translators']
    if translators:
        for i, (first, last) in enumerate(translators):
            translators[i] = first, last + ' (مترجم)'
        # Todo: add a 'Translated by ' before name of translators?
        others = d['others']
        if others:
            others.extend(d['translators'])
        else:
            d['others'] = d['translators']
    others = d['others']
    if others:
        cit += names1para(others, 'others')

    if cite_type == 'book':
        booktitle = d['booktitle'] or d['container-title']
    else:
        booktitle = None

    if booktitle:
            cit += ' | title=' + booktitle
            if title:
                cit += ' | chapter=' + title
    elif title:
        cit += ' | title=' + title

    if journal:
        cit += ' | journal=' + journal
    elif website:
        cit += ' | website=' + website

    chapter = d['chapter']
    if chapter:
        cit += ' | chapter=' + chapter

    publisher = d['publisher'] or d['organization']
    if publisher:
        cit += ' | publisher=' + publisher

    address = d['address'] or d['publisher-location']
    if address:
        cit += ' | publication-place=' + address

    edition = d['edition']
    if edition:
        cit += ' | edition=' + edition

    series = d['series']
    if series:
        cit += ' | series=' + series

    volume = d['volume']
    if volume:
        cit += ' | volume=' + volume.translate(DIGITS_TO_EN)

    issue = d['issue'] or d['number']
    if issue:
        cit += ' | issue=' + issue

    date = d['date']
    if date:
        if not isinstance(date, str):
            date = date.strftime(date_format)
        cit += ' | date=' + date

    year = d['year']
    if year:
        year = str(int(year))  # convert any non-Latin digits to English ones
        if not date or year not in date:
            cit += ' | year=' + year
        sfn += ' | ' + year

    isbn = d['isbn']
    if isbn:
        cit += ' | isbn=' + isbn

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

    pages = d['page']
    if pages:
        if '–' in pages:
            sfn += ' | pp=' + pages
        else:
            sfn += ' | p=' + pages
    if cite_type == 'journal':
        if pages:
            if '–' in pages:
                cit += ' | pages=' + pages
            else:
                cit += ' | page=' + pages

    url = d['url']
    if url:
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not DOI_URL_MATCH(url):
            cit += ' | url=' + url
        else:
            # To prevent addition of access date
            url = None

    if not pages and cite_type != 'web':
        sfn += ' | p='

    archive_url = d['archive-url']
    if archive_url:
        cit += (
            ' | archive-url=' + archive_url +
            ' | archive-date=' + d['archive-date'].strftime(date_format) +
            ' | url-status=' + d['url-status']
        )

    language = d['language']
    if language:
        language = TO_TWO_LETTER_CODE(language.lower(), language)
        if language.lower() != 'en':
            cit += ' | language=' + language

    # Todo: Template:Citation generates anchors for Harvard by default
    # references
    #   whereas the Cite templates by default do not (although they can be
    # made to
    #   do so).
    if authors:
        cit += ' | ref=harv'
    else:
        # order should match sfn_template
        cit += ' | ref={{sfnref | ' +\
             (publisher or journal or website or title or 'Anon.')
        if year:
            cit += ' | ' + year
        cit += '}}'

    if url:
        cit += ' | access-date=' + datetime_date.today().strftime(date_format)

    cit += '}}'
    sfn += '}}'
    # Finally create the ref tag.
    name = sfn[8:-2].replace(' | ', ' ').replace("'", '')
    text = refless(cit[2:])
    if ' p=' in name and ' | page=' not in text:
        name = name.replace(' p=', ' p. ')
        if pages:
            text = text[:-2] + ' | page=' + pages + '}}'
        else:
            text = text[:-2] + ' | page=}}'
    elif ' pp=' in name:
        name = name.replace(' pp=', ' pp. ')
        if pages and ' | pages=' not in text:
            text = text[:-2] + ' | pages=' + pages + '}}'
    ref = '&lt;ref name="' + name + '"&gt;' + text + '&lt;/ref&gt;'
    return sfn, cit, ref


def names2para(names, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    c = 0
    s = ''
    for first, last in names:
        c += 1
        if c == 1:
            if first or not nofn_parameter:
                s += ' | ' + ln_parameter + '=' + last
                s += ' | ' + fn_parameter + '=' + first
            else:
                s += ' | ' + nofn_parameter + '=' + fullname(first, last)
        else:
            if first or not nofn_parameter:
                s += ' | ' + ln_parameter + str(c) + '=' + last
                s += ' | ' + fn_parameter + str(c) + '=' + first
            else:
                s += ' | ' + nofn_parameter + str(c) + '=' + \
                     fullname(first, last)
    return s


def names1para(translators, para):
    """Take list of names. Return the string to be appended to citation."""
    s = ' | ' + para + '='
    c = 0
    for first, last in translators:
        c += 1
        if c == 1:
            s += fullname(first, last)
        elif c == len(translators):
            s += ', and ' + fullname(first, last)
        else:
            s += ', ' + fullname(first, last)
    return s


def fullname(first: str, last: str) -> str:
    if first:
        return first + ' ' + last
    return last


logger = getLogger(__name__)
