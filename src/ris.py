#! /usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict

from regex import compile as regex_compile, MULTILINE, VERBOSE

from src.doi import DOI_SEARCH
from src.commons import RawName, InvalidNameError


RIS_FULLMATCH = regex_compile(
    r'''
    (?: # this  group matches any line
        ^
        (?>
            A[U\d]\ {2}-\ (?<author>.++)
            |DA\ {2}-\ \d++/(?<month>\d++).*+
            |EP\ {2}-\ (?<end_page>.++)
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
            |T(?>
                [1I]\ {2}-\ (?<title>.++)
                |3\ {2}-\ (?<series>.++)
                |Y\ {2}-\ (?<type>.++)
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
    VERBOSE | MULTILINE,
).fullmatch


def parse(ris_text):
    """Parse RIS_text data and return the result as a dictionary."""
    d = defaultdict(lambda: None)
    match = RIS_FULLMATCH(ris_text)
    d.update(match.groupdict())
    # cite_type: (book, journal, . . . )
    d['cite_type'] = d['type'].lower()
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
    # DOIs may be in N1 (notes) tag, search for it in any tag
    m = DOI_SEARCH(ris_text)
    if m:
        d['doi'] = m[0]
    start_page = d['start_page']
    if start_page:
        end_page = d['end_page']
        if end_page:
            d['page'] = start_page + '–' + end_page
        else:
            d['page'] = start_page
    # in IRS, url can be seprated using a ";"
    d['url'] = d['url'].partition(';')[0]
    return d
