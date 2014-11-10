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

import commons


def search_for_tag(bibtex):
    """Find all tags in the bibtex and return result as a dictionary."""
    d = {}
    fs = re.findall('(\w+)\s*=\s*(?:[{"]\s*(.*?)\s*["}]|(\d+))', bibtex)
    for f in fs:
        d[f[0].lower()] = f[1] if f[1] else f[2]
    return d


def parse(bibtex):
    """Parse bibtex string and return a dictionary of information."""
    bibtex = replace_specials(bibtex)
    d = search_for_tag(bibtex)
    # type: (book, journal, . . . )
    m = re.search('@(.*?)\s*\{', bibtex, re.I)
    if m:
        d['type'] = m.group(1).strip().lower()
    # author
    if 'author' in d:
        d['authors'] = []
        for author in d['author'].split(' and '):
            if author.endswith(' and'):
                author = author[:-4]
            if not author:
                continue
            name = commons.Name(author)
            d['authors'].append(name)
        del d['author']
    if 'number' in d:
        d['issue'] = d['number']
        del d['number']
    if 'pages' in d:
        d['pages'] = d['pages'].replace(
            ' ', ''
        ).replace(
            '--', '–'
        ).replace(
            '-', '–'
        )
        if '–' in d['pages']:
            d['startpage'], d['endpage'] = d['pages'].split('–')
    return d


def replace_specials(bibtex):
    """Replace common TeX special symbol commonds with their unicode value."""
    bibtex = bibtex.replace(r'{\textregistered}', '®')
    bibtex = bibtex.replace(r'\%', '%')
    bibtex = bibtex.replace(r'\$', '$')
    bibtex = bibtex.replace(r'\{', '{')
    bibtex = bibtex.replace(r'\}', '}')
    bibtex = bibtex.replace(r'\#', '#')
    bibtex = bibtex.replace(r'\&', '&')
    bibtex = bibtex.replace(r'{\={a}}', 'ā')
    bibtex = bibtex.replace(r'{\v{c}}', 'č')
    bibtex = bibtex.replace(r'{\={e}}', 'ē')
    bibtex = bibtex.replace(r'{\v{g}}', 'ģ')
    bibtex = bibtex.replace(r'{\={\i}}', 'ī')
    bibtex = bibtex.replace(r'{\c{k}}', 'ķ')
    bibtex = bibtex.replace(r'{\c{l}}', 'ļ')
    bibtex = bibtex.replace(r'{\c{n}}', 'ņ')
    bibtex = bibtex.replace(r'{\v{s}}', 'š')
    bibtex = bibtex.replace(r'{\={u}}', 'ū')
    bibtex = bibtex.replace(r'{\v{z}}', 'ž')
    bibtex = bibtex.replace(r'{\={A}}', 'Ā')
    bibtex = bibtex.replace(r'{\v{C}}', 'Č')
    bibtex = bibtex.replace(r'{\={E}}', 'Ē')
    bibtex = bibtex.replace(r'{\c{G}}', 'Ģ')
    bibtex = bibtex.replace(r'{\={I}}', 'Ī')
    bibtex = bibtex.replace(r'{\c{K}}', 'Ķ')
    bibtex = bibtex.replace(r'{\c{L}}', 'Ļ')
    bibtex = bibtex.replace(r'{\c{N}}', 'Ņ')
    bibtex = bibtex.replace(r'{\v{S}}', 'Š')
    bibtex = bibtex.replace(r'{\={U}}', 'Ū')
    bibtex = bibtex.replace(r'{\v{Z}}', 'Ž')
    return bibtex
    
