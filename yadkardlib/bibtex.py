#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re

#Known issues: currently it does not detect special symbols and escapes
#more information: http://www.bibtex.org/SpecialSymbols/
#cases: '\_' in urls and '\&' in titles

def parse(bibtex_text):
    '''Parses bibtex_text data and returns a dictionary of information'''
    #replacing common latex special commonds:
    bibtex_text = bibtex_text.replace('\%', '%')
    bibtex_text = bibtex_text.replace('\$', '$')
    bibtex_text = bibtex_text.replace('\{', '{')
    bibtex_text = bibtex_text.replace('\}', '}')
    bibtex_text = bibtex_text.replace('\#', '#')
    bibtex_text = bibtex_text.replace('\&', '&')
    bibtex_text = bibtex_text.replace('\_', '_')
    d = {}
    #type: (book, journal, . . . )
    m = re.search('@(.*?)\s*\{', bibtex_text, re.I)
    if m:
        d['type'] = m.group(1).strip()
    #citation-key:
    m = re.search('@.*?{\s*(.*?)\s*,', bibtex_text, re.I)
    if m:
        d['citation-key'] = m.group(1).strip()
    #author:
    m = re.search('author\s*=\s*\{\s*(.*?)\\s*}', bibtex_text, re.I)
    if m:
        d['authors'] = m.group(1).strip()
        #author parameter needs to be parsed itself:
        if ' and ' in d['authors']:
            author_list = d['authors'].split(' and ')
        else:
            author_list = [d['authors']]
        d['lastnames'] = []
        d['firstnames'] = []
        for author in author_list:
            if ',' in author:
                lastname, firstname = author.split(',')
            else:
                lastname, fistname = author, ''
            d['lastnames'].append(lastname.strip())
            d['firstnames'].append(firstname.strip())
        
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
