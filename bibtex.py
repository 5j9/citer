#! /usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used for parsing BibTeX entries.

The goal of this code is to parse BibTeX entries from a number of known sites
with known BibTeX formats; therefore many other BiBteX entries may be parsed
incorrectly or incompletely as TeX system is very complex and this module is
not intended to parse TeX.

Some of the known issues:
    * Currently it does not detect special symbols and many TeX escape
        sequences (more information: http://www.bibtex.org/SpecialSymbols/)
    * String concatinatins are not recognized. (e.g. "str1" # "str2")
    * Abbreviations are not supported (e.g. @string { foo = "Mrs. Foo" })
"""


import re

from commons import Name


def search_for_tag(bibtex):
    """Find all tags in the bibtex and return result as a dictionary."""
    fs = re.findall('(\w+)\s*=\s*(?:[{"]\s*(.*?)\s*["}]|(\d+))', bibtex)
    return {f[0].lower(): f[1] if f[1] else f[2] for f in fs}


def parse(bibtex):
    """Parse bibtex string and return a dictionary of information."""
    bibtex = replace_specials(bibtex)
    d = search_for_tag(bibtex)
    # type: (book, journal, . . . )
    m = re.search('@(.*?)\s*\{', bibtex, re.I)
    if m:
        d['type'] = m.group(1).strip().lower()
    # author
    author = d.get('author')
    if author:
        names = []
        d['authors'] = names
        for author in author.split(' and '):
            if author.endswith(' and'):
                author = author[:-4]
            if not author:
                continue
            name = Name(author)
            names.append(name)
        del d['author']
    number = d.get('number')
    if number:
        d['issue'] = number
        del d['number']
    pages = d.get('pages')
    if pages:
        pages = d['pages'] = (
            pages.replace(' ', '').replace('--', '–').replace('-', '–')
        )
        startpage, sep, endpage = pages.partition('–')
        if sep:
            d['startpage'], d['endpage'] = startpage, endpage
    return d


def replace_specials(bibtex):
    """Replace common TeX special symbol commonds with their unicode value."""
    return (
        bibtex
        .replace(r'{\textregistered}', '®')
        .replace(r'\%', '%')
        .replace(r'\$', '$')
        .replace(r'\{', '{')
        .replace(r'\}', '}')
        .replace(r'\#', '#')
        .replace(r'\&', '&')
        .replace(r'{\={a}}', 'ā')
        .replace(r'{\v{c}}', 'č')
        .replace(r'{\={e}}', 'ē')
        .replace(r'{\v{g}}', 'ģ')
        .replace(r'{\={\i}}', 'ī')
        .replace(r'{\c{k}}', 'ķ')
        .replace(r'{\c{l}}', 'ļ')
        .replace(r'{\c{n}}', 'ņ')
        .replace(r'{\v{s}}', 'š')
        .replace(r'{\={u}}', 'ū')
        .replace(r'{\v{z}}', 'ž')
        .replace(r'{\={A}}', 'Ā')
        .replace(r'{\v{C}}', 'Č')
        .replace(r'{\={E}}', 'Ē')
        .replace(r'{\c{G}}', 'Ģ')
        .replace(r'{\={I}}', 'Ī')
        .replace(r'{\c{K}}', 'Ķ')
        .replace(r'{\c{L}}', 'Ļ')
        .replace(r'{\c{N}}', 'Ņ')
        .replace(r'{\v{S}}', 'Š')
        .replace(r'{\={U}}', 'Ū')
        .replace(r'{\v{Z}}', 'Ž')
    )
