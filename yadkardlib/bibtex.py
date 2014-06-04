#! /data/project/yadkard/venv/bin python
# -*- coding: utf-8 -*-

import re

import conv

#Known issues: currently it does not detect special symbols and escapes
#more information: http://www.bibtex.org/SpecialSymbols/
#cases: '\_' in urls and '\&' in titles

def parse(bibtex_text):
    '''Parse bibtex_text data and return a dictionary of information.'''
    #replacing common latex special commonds:
    bibtex_text = bibtex_text.replace(r'{\textregistered}', u'®')
    bibtex_text = bibtex_text.replace(r'\%', '%')
    bibtex_text = bibtex_text.replace(r'\$', '$')
    bibtex_text = bibtex_text.replace(r'\{', '{')
    bibtex_text = bibtex_text.replace(r'\}', '}')
    bibtex_text = bibtex_text.replace(r'\#', '#')
    bibtex_text = bibtex_text.replace(r'\&', '&')
    bibtex_text = bibtex_text.replace(r'{\={a}}', u'ā')
    bibtex_text = bibtex_text.replace(r'{\v{c}}', u'č')
    bibtex_text = bibtex_text.replace(r'{\={e}}', u'ē')
    bibtex_text = bibtex_text.replace(r'{\v{g}}', u'ģ')
    bibtex_text = bibtex_text.replace(r'{\={\i}}', u'ī')
    bibtex_text = bibtex_text.replace(r'{\c{k}}', u'ķ')
    bibtex_text = bibtex_text.replace(r'{\c{l}}', u'ļ')
    bibtex_text = bibtex_text.replace(r'{\c{n}}', u'ņ')
    bibtex_text = bibtex_text.replace(r'{\v{s}}', u'š')
    bibtex_text = bibtex_text.replace(r'{\={u}}', u'ū')
    bibtex_text = bibtex_text.replace(r'{\v{z}}', u'ž')
    bibtex_text = bibtex_text.replace(r'{\={A}}', u'Ā')
    bibtex_text = bibtex_text.replace(r'{\v{C}}', u'Č')
    bibtex_text = bibtex_text.replace(r'{\={E}}', u'Ē')
    bibtex_text = bibtex_text.replace(r'{\c{G}}', u'Ģ')
    bibtex_text = bibtex_text.replace(r'{\={I}}', u'Ī')
    bibtex_text = bibtex_text.replace(r'{\c{K}}', u'Ķ')
    bibtex_text = bibtex_text.replace(r'{\c{L}}', u'Ļ')
    bibtex_text = bibtex_text.replace(r'{\c{N}}', u'Ņ')
    bibtex_text = bibtex_text.replace(r'{\v{S}}', u'Š')
    bibtex_text = bibtex_text.replace(r'{\={U}}', u'Ū')
    bibtex_text = bibtex_text.replace(r'{\v{Z}}', u'Ž')
    d = {}
    #type: (book, journal, . . . )
    m = re.search('@(.*?)\s*\{', bibtex_text, re.I)
    if m:
        d['type'] = m.group(1).strip().lower()
    #author:
    m = re.search('author\s*=\s*\{\s*(.*?)\\s*}', bibtex_text, re.I)
    if m:
        d['authors'] = []
        authors = m.group(1).split(' and ')
        for author in authors:
            name = conv.Name(author, ',')
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
        d['number'] = m.group(1).strip()
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
        d['pages'] = d['pages'].replace('--', u'–')
        d['pages'] = d['pages'].replace('-', u'–')
        if u'–' in d['pages']:
            d['startpage'], d['endpage'] = d['pages'].split(u'–')
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
