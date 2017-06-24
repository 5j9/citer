#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes required to create English Wikipedia citation templates."""


import re
from datetime import date as datetime_date
from collections import defaultdict
from logging import getLogger


# Includes ShortDOIs (See: http://shortdoi.org/) and
# https://www.crossref.org/display-guidelines/
DOI_URL_MATCH = re.compile(
    r'https?://(dx\.)?doi\.org/'
).match

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


def citations(d: defaultdict) -> tuple:
    """Create citation templates according to the given dictionary."""
    date_format = d['date_format']
    cite_type = TYPE_TO_CITE(d['cite_type'])
    if not cite_type:
        logger.warning(f'Unknown citation type: {cite_type}, d: {d}')
        cite_type = ''
    cite = '* {{cite ' + cite_type
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
        cite += names2para(authors, 'first', 'last', 'author')
        # {{sfn}} only supports a maximum of four authors
        for author in authors[:4]:
            sfn += ' | ' + author.lastname
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
        cite += names2para(editors, 'editor-first', 'editor-last', 'editor')
    translators = d['translators']
    if translators:
        for translator in translators:
            translator.fullname += ' (مترجم)'
        # todo: add a 'Translated by ' before name of translators
        others = d['others']
        if others:
            others.extend(d['translators'])
        else:
            d['others'] = d['translators']
    others = d['others']
    if others:
        cite += names1para(others, 'others')

    if cite_type == 'book':
        booktitle = d['booktitle'] or d['container-title']
    else:
        booktitle = None

    if booktitle:
            cite += ' | title=' + booktitle
            if title:
                cite += ' | chapter=' + title
    elif title:
        cite += ' | title=' + title

    if journal:
        cite += ' | journal=' + journal
    elif website:
        cite += ' | website=' + website

    chapter = d['chapter']
    if chapter:
        cite += ' | chapter=' + chapter

    publisher = d['publisher'] or d['organization']
    if publisher:
        cite += ' | publisher=' + publisher

    address = d['address'] or d['publisher-location']
    if address:
        cite += ' | publication-place=' + address

    edition = d['edition']
    if edition:
        cite += ' | edition=' + edition

    series = d['series']
    if series:
        cite += ' | series=' + series

    volume = d['volume']
    if volume:
        cite += ' | volume=' + volume

    issue = d['issue'] or d['number']
    if issue:
        cite += ' | issue=' + issue

    date = d['date']
    if date:
        if not isinstance(date, str):
            date = date.strftime(date_format)
        cite += ' | date=' + date

    year = d['year']
    if year:
        if not date or year not in date:
            cite += ' | year=' + year
        sfn += ' | ' + year

    isbn = d['isbn']
    if isbn:
        cite += ' | isbn=' + isbn

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
    if pages:
        if '–' in pages:
            sfn += ' | pp=' + pages
        else:
            sfn += ' | p=' + pages
    if cite_type == 'journal':
        if pages:
            if '–' in pages:
                cite += ' | pages=' + pages
            else:
                cite += ' | page=' + pages

    url = d['url']
    if url:
        # Don't add a DOI URL if we already have added a DOI.
        if not doi or not DOI_URL_MATCH(url):
            cite += ' | url=' + url
        else:
            # To prevent addition of access date
            url = None

    if not pages and cite_type != 'web':
        sfn += ' | p='

    archive_url = d['archive-url']
    if archive_url:
        cite += (
            ' | archive-url=' + archive_url +
            ' | archive-date=' + d['archive-date'].strftime(date_format) +
            ' | dead-url=' + d['dead-url']
        )

    language = d['language']
    if language:
        if language.lower() not in ('english', 'en'):
            cite += ' | language=' + language

    # Todo: Template:Citation by default generates anchors for Harvard
    # references
    #   whereas the Cite templates by default do not (although they can be
    # made to
    #   do so).
    if authors:
        cite += ' | ref=harv'
    else:
        # order should match sfn_template
        cite += ' | ref={{sfnref | ' +\
             (publisher or journal or website or title or 'Anon.')
        if year:
            cite += ' | ' + year
        cite += '}}'

    if url:
        cite += ' | access-date=' + datetime_date.today().strftime(date_format)

    cite += '}}'
    sfn += '}}'
    # Finally create the ref tag.
    name = sfn[8:-2].replace(' | ', ' ').replace("'", '')
    text = re.sub(
        r'( \| ref=({{.*?}}|harv))(?P<repl> \| |}})',
        r'\g<repl>',
        cite[2:],
    )
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
    return cite, sfn, ref


def names2para(names, fn_parameter, ln_parameter, nofn_parameter=None):
    """Take list of names. Return the string to be appended to citation."""
    c = 0
    s = ''
    for name in names:
        c += 1
        if c == 1:
            if name.firstname or not nofn_parameter:
                s += ' | ' + ln_parameter + '=' + name.lastname
                s += ' | ' + fn_parameter + '=' + name.firstname
            else:
                s += ' | ' + nofn_parameter + '=' + name.fullname
        else:
            if name.firstname or not nofn_parameter:
                s += ' | ' + ln_parameter + str(c) + '=' + name.lastname
                s += ' | ' + fn_parameter + str(c) + '=' + name.firstname
            else:
                s += ' | ' + nofn_parameter + str(c) + '=' + name.fullname
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
            s += ', and ' + name.fullname
        else:
            s += ', ' + name.fullname
    return s

logger = getLogger(__name__)