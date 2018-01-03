#! /usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict

from regex import compile as regex_compile, VERBOSE

from src.doi import DOI_SEARCH
from src.commons import RawName, InvalidNameError


RIS_FULLMATCH = regex_compile(
    r'''
    (?: # this  group matches any line
        (?>
            A[U\d]\ {2}-\ (?<author>.++)
            |DA\ {2}-\ \d++/(?<month>\d++).*+
            |EP\ {2}-\ (?<end_page>.++)
            |T(?>
                [1I]\ {2}-\ (?<title>.++)
                |3\ {2}-\ (?<series>.++)
                |Y\ {2}-\ (?<type>.++)
            )
            |IS\ {2}-\ (?<issue>.++)
            |J[FA]\ {2}-\ (?<journal>.++)
            |LA\ {2}-\ (?<language>.++)
            |P(?>
                B\ {2}-\ (?<publisher>.++)
                |Y\ {2}-\ (?<year>\d++).*+
            )
            |S(?>
                N\ {2}-\ (?<isbn>.++)
                |P\ {2}-\ (?<start_page>.++)
            )
            |UR\ {2}-\ (?<url>.++)
            |VL\ {2}-\ (?<volume>.++)
            |Y1\ {2}-\ (?<year>\d++).*+
            # any other line
            |[^\n]*+
        )
        \n
    )*
    ''',
    VERBOSE,
).fullmatch


def parse(ris_text):
    """Parse RIS_text data and return the result as a dictionary."""
    d = defaultdict(lambda: None)
    # cite_type: (book, journal, . . . )
    match = RIS_FULLMATCH(ris_text)
    groupdict_get = match.groupdict().get
    type_ = groupdict_get('type')
    if type_:
        d['cite_type'] = type_.lower()
    # author:
    # d['authors'] should not be created unless there are some authors
    authors = match.captures('author')
    if authors:
        d['authors'] = []
        for author in authors:
            try:
                author = RawName(author)
            except InvalidNameError:
                continue
            else:
                d['authors'].append(author)
    title = groupdict_get('title')
    if title:
        d['title'] = title
    series = groupdict_get('series')
    if series:
        d['series'] = series
    publisher = groupdict_get('publisher')
    if publisher:
        d['publisher'] = publisher
    journal = groupdict_get('journal')
    if journal:
        d['journal'] = journal
    issue = groupdict_get('issue')
    if issue:
        d['issue'] = issue
    volume = groupdict_get('volume')
    if volume:
        d['volume'] = volume
    year = groupdict_get('year')
    if year:
        d['year'] = year
    month = groupdict_get('month')
    if month:
        d['month'] = month
    isbn = groupdict_get('isbn')
    if isbn:
        d['isbn'] = isbn
    # DOIs may be in N1 (notes) tag, search for it in any tag
    m = DOI_SEARCH(ris_text)
    if m:
        d['doi'] = m[0]
    start_page = groupdict_get('start_page')
    if start_page:
        end_page = groupdict_get('end_page')
        if end_page:
            d['page'] = start_page + '–' + end_page
        else:
            d['page'] = start_page
    url = groupdict_get('url')
    if url:
        # in IRS, url can be seprated using a ";"
        d['url'] = url.partition(';')[0]
    language = groupdict_get('language')
    if language:
        d['language'] = language
    return d
