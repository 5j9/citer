#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

import re
from doi import doi_regex

import conv

def parse(ris_text):
    """Parse RIS_text data and return the result as a dictionary."""
    d = {}
    #type: (book, journal, . . . )
    m = re.search('TY  - (.*)', ris_text)
    if m:
        d['type'] = m.group(1).strip().lower()
    #author:
    m = re.findall('(:?AU|A\d)  - (.*)', ris_text)
    #d['authors'] should not be created unless there are some authors
    if m:
        d['authors'] = []
        for match in m:
            name = conv.Name(match[1], ',')
            d['authors'].append(name)
            
    m = re.search('(T1|TI)  - (.*)', ris_text)
    if m:
        if m.group(2):
            d['title'] = m.group(2).strip()
    m = re.search('T3  - (.*)', ris_text)
    if m:
        d['series'] = m.group(1).strip()
    m = re.search('PB  - (.*)', ris_text)
    if m:
        d['publisher'] = m.group(1).strip()
    m = re.search('(JF|JA)  - (.*)', ris_text)
    if m:
        if m.group(2):
            d['journal'] = m.group(2).strip()
    m = re.search('IS  - (.*)', ris_text)
    if m:
        d['issue'] = m.group(1).strip()
    m = re.search('VL  - (.*)', ris_text)
    if m:
        d['volume'] = m.group(1).strip()
    m = re.search('(PY|Y1|DA)  - (\d*)', ris_text)
    if m:
        if m.group(2):
            d['year'] = m.group(2).strip()
    m = re.search('(PY|Y1|DA)  - \d+/(\d*)', ris_text)
    if m:
        if m.group(2):
            d['month'] = m.group(2).strip()
    m = re.search('SN  - (.*)', ris_text)
    if m:
        d['isbn'] = m.group(1).strip()
    #DOIs may be in N1 (notes) tag, search for it in any tag
    m = re.search(doi_regex, ris_text)
    if m:
        d['doi'] = m.group(0).strip()
    m = re.search('SP  - (.*)', ris_text)
    if m:
        d['startpage'] = m.group(1).strip()
        d['pages'] = d['startpage']
    m = re.search('EP  - (.*)', ris_text)
    if m:
        d['endpage'] = m.group(1).strip()
        d['pages'] = d['startpage'] + u'–' + d['endpage']
    m = re.search('UR  - (.*)', ris_text)
    if m:
        #in IRS, url can be seprated using a ";"
        d['url'] = m.group(1).split(';')[0].strip()
    m = re.search('LA  - (.*)', ris_text)
    if m:
        d['language'] =  m.group(1).strip()
    return d
