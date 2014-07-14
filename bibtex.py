#! /usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used for parsing BibTeX entries.

Known issues:
    * Currently it does not detect special symbols and many TeX escape
        sequences (more information: http://www.bibtex.org/SpecialSymbols/)
"""

import re

import commons




def parse(bibtex_text):
    """Parse bibtex_text data and return a dictionary of information."""
    # replacing common latex special symbols commonds
    bibtex_text = bibtex_text.replace(r'{\textregistered}', '®')
    bibtex_text = bibtex_text.replace(r'\%', '%')
    bibtex_text = bibtex_text.replace(r'\$', '$')
    bibtex_text = bibtex_text.replace(r'\{', '{')
    bibtex_text = bibtex_text.replace(r'\}', '}')
    bibtex_text = bibtex_text.replace(r'\#', '#')
    bibtex_text = bibtex_text.replace(r'\&', '&')
    bibtex_text = bibtex_text.replace(r'{\={a}}', 'ā')
    bibtex_text = bibtex_text.replace(r'{\v{c}}', 'č')
    bibtex_text = bibtex_text.replace(r'{\={e}}', 'ē')
    bibtex_text = bibtex_text.replace(r'{\v{g}}', 'ģ')
    bibtex_text = bibtex_text.replace(r'{\={\i}}', 'ī')
    bibtex_text = bibtex_text.replace(r'{\c{k}}', 'ķ')
    bibtex_text = bibtex_text.replace(r'{\c{l}}', 'ļ')
    bibtex_text = bibtex_text.replace(r'{\c{n}}', 'ņ')
    bibtex_text = bibtex_text.replace(r'{\v{s}}', 'š')
    bibtex_text = bibtex_text.replace(r'{\={u}}', 'ū')
    bibtex_text = bibtex_text.replace(r'{\v{z}}', 'ž')
    bibtex_text = bibtex_text.replace(r'{\={A}}', 'Ā')
    bibtex_text = bibtex_text.replace(r'{\v{C}}', 'Č')
    bibtex_text = bibtex_text.replace(r'{\={E}}', 'Ē')
    bibtex_text = bibtex_text.replace(r'{\c{G}}', 'Ģ')
    bibtex_text = bibtex_text.replace(r'{\={I}}', 'Ī')
    bibtex_text = bibtex_text.replace(r'{\c{K}}', 'Ķ')
    bibtex_text = bibtex_text.replace(r'{\c{L}}', 'Ļ')
    bibtex_text = bibtex_text.replace(r'{\c{N}}', 'Ņ')
    bibtex_text = bibtex_text.replace(r'{\v{S}}', 'Š')
    bibtex_text = bibtex_text.replace(r'{\={U}}', 'Ū')
    bibtex_text = bibtex_text.replace(r'{\v{Z}}', 'Ž')
    d = {}
    # type: (book, journal, . . . )
    m = re.search('@(.*?)\s*\{', bibtex_text, re.I)
    if m:
        d['type'] = m.group(1).strip().lower()
    # author
    m = re.search('author\s*=\s*\{\s*(.*?)\\s*}', bibtex_text, re.I)
    if m:
        d['authors'] = []
        authors = m.group(1).split(' and ')
        for author in authors:
            name = commons.Name(author)
            d['authors'].append(name)

    m = re.search('title\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['title'] = m.group(1).strip()
    m = re.search('publisher\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['publisher'] = m.group(1).strip()
    m = re.search('journal\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['journal'] = m.group(1).strip()
    m = re.search('number\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['issue'] = m.group(1).strip()
    m = re.search('series\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['series'] = m.group(1).strip()
    m = re.search('volume\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['volume'] = m.group(1).strip()
    m = re.search('year\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['year'] = m.group(1).strip()
    m = re.search('month\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['month'] = m.group(1).strip()
    m = re.search('isbn\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['isbn'] = m.group(1).strip()
    m = re.search('lccn\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['lccn'] = m.group(1).strip()
    m = re.search('pages\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['pages'] = m.group(1).strip()
        d['pages'] = d['pages'].replace('--', '–')
        d['pages'] = d['pages'].replace('-', '–')
        if '–' in d['pages']:
            d['startpage'], d['endpage'] = d['pages'].split('–')
    m = re.search('url\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['url'] = m.group(1).strip()
    m = re.search('doi\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['doi'] = m.group(1).strip()
    m = re.search('address\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['address'] = m.group(1).strip()
    m = re.search('language\s*=\s*\{\s*(.*?)\s*\}', bibtex_text, re.I)
    if m:
        d['language'] = m.group(1).strip()
    return d
