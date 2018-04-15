#! /usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict

from regex import compile as regex_compile, MULTILINE, VERBOSE

from src.doi import DOI_SEARCH
from src.commons import first_last, InvalidNameError


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
                N\ {2}-\ (?<isbn>\S*+).*+
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
    cite_type = d['type'].lower()
    url = d['url']
    if cite_type == 'elec' and url:
        d['cite_type'] = 'web'
    else:
        d['cite_type'] = cite_type
    # author:
    # d['authors'] should not be created unless there are some authors
    authors = match.captures('author')
    if authors:
        # From RIS Format Specifications:
        # Each author must be on a separate line, preceded by this tag. Each
        # reference can contain unlimited author fields, and can contain up
        # to 255 characters for each field.
        # The author name must be in the following syntax:
        # Lastname,Firstname,Suffix
        # For Firstname, you can use full names, initials, or both.
        d['authors'] = []
        for author in authors:
            try:
                author = first_last(author, separator=',')
            except InvalidNameError:
                continue
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
    # in IRS, url can be separated using a ";"
    if url:
        d['url'] = url.partition(';')[0]
    return d
