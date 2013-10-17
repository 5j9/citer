#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
from doi import pattern as doi_pattern

def parse(ris_text):
    '''Parses RIS_text data and returns a dictionary of information'''
    d = {}
    #type: (book, journal, . . . )
    m = re.search('TY  - (.*)', ris_text)
    if m:
        d['type'] = m.group(1).strip()
    #author:
    m = re.findall('(:?AU|A\d)  - (.*)', ris_text)
    #d['authors'] should not be created unless there are some authors
    if m:
        d['authors'] = []
        for author in m:
            d['authors'].append(author[1])
        #author parameter needs to be parsed itself:
        d['lastnames'] = []
        d['firstnames'] = []
        for author in d['authors']:
            if ',' in author:
                lastname, firstname = author.split(',')
            else:
                lastname, firstname = author, ''
            d['lastnames'].append(lastname.strip())
            d['firstnames'].append(firstname.strip())
            
    m = re.search('(T1|TI)  - (.*)', ris_text)
    if m:
        if m.group(2):
            d['title'] = m.group(2).strip()
    m = re.search('PB  - (.*)', ris_text)
    if m:
        d['publisher'] = m.group(1).strip()
    m = re.search('(JF|JA)  - (.*)', ris_text)
    if m.group(2):
        if m.group(2):
            d['journal'] = m.group(2).strip()
    m = re.search('IS  - (.*)', ris_text)
    if m:
        d['number'] = m.group(1).strip()
    m = re.search('VL  - (.*)', ris_text)
    if m:
        d['volume'] = m.group(1).strip()
    m = re.search('(PY|Y1|DA)  - (\d*)', ris_text)
    if m.group(2):
        if m.group(2):
            d['year'] = m.group(2).strip()
    m = re.search('(PY|Y1|DA)  - \d+/(\d*)', ris_text)
    if m.group(2):
        if m.group(2):
            d['month'] = m.group(2).strip()
    m = re.search('SN  - (.*)', ris_text)
    if m:
        d['isbn'] = m.group(1).strip()
    #DOIs may be in N1 (notes) tag, search for it in any tag
    m = re.search(doi_pattern, ris_text)
    if m:
        d['doi'] = m.group(0).strip()
    m = re.search('SP  - (.*)', ris_text)
    if m:
        d['startpage'] = m.group(1).strip()
        d['pages'] = d['startpage']
    m = re.search('EP  - (.*)', ris_text)
    if m:
        d['endpage'] = m.group(1).strip()
        d['pages'] = d['startpage'] + '–' + d['endpage']
    m = re.search('UR  - (.*)', ris_text)
    if m:
        #in IRS, url can be seprated using a ";"
        d['url'] = m.group(1).split(';')[0].strip()
    m = re.search('LA  - (.*)', ris_text)
    if m:
        d['language'] =  m.group(1).strip()
    return d
