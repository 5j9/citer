#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
from doi import DOI_SEARCH

from commons import Name, InvalidNameError


TY_SEARCH = re.compile('TY  - (.*)').search
AU_FINDALL = re.compile('(:?AU|A\d)  - (.*)').findall
T1_SEARCH = re.compile('(T1|TI)  - (.*)').search
T3_SEARCH = re.compile('T3  - (.*)').search
PB_SEARCH = re.compile('PB  - (.*)').search
JF_SEARCH = re.compile('(JF|JA)  - (.*)').search
IS_SEARCH = re.compile('IS  - (.*)').search
VL_SEARCH = re.compile('VL  - (.*)').search
PY_SEARCH = re.compile('(PY|Y1|DA)  - (\d*)').search
DA_SEARCH = re.compile('(PY|Y1|DA)  - \d+/(\d*)').search
SN_SEARCH = re.compile('SN  - (.*)').search
SP_SEARCH = re.compile('SP  - (.*)').search
EP_SEARCH = re.compile('EP  - (.*)').search
UR_SEARCH = re.compile('UR  - (.*)').search
LA_SEARCH = re.compile('LA  - (.*)').search


def parse(ris_text):
    """Parse RIS_text data and return the result as a dictionary."""
    d = {}
    # type: (book, journal, . . . )
    m = TY_SEARCH(ris_text)
    if m:
        d['type'] = m.group(1).strip().lower()
    # author:
    m = AU_FINDALL(ris_text)
    # d['authors'] should not be created unless there are some authors
    if m:
        d['authors'] = []
        for match in m:
            try:
                name = Name(match[1])
            except InvalidNameError:
                continue
            d['authors'].append(name)

    m = T1_SEARCH(ris_text)
    if m:
        if m.group(2):
            d['title'] = m.group(2).strip()
    m = T3_SEARCH(ris_text)
    if m:
        d['series'] = m.group(1).strip()
    m = PB_SEARCH(ris_text)
    if m:
        d['publisher'] = m.group(1).strip()
    m = JF_SEARCH(ris_text)
    if m:
        if m.group(2):
            d['journal'] = m.group(2).strip()
    m = IS_SEARCH(ris_text)
    if m:
        d['issue'] = m.group(1).strip()
    m = VL_SEARCH(ris_text)
    if m:
        d['volume'] = m.group(1).strip()
    m = PY_SEARCH(ris_text)
    if m:
        if m.group(2):
            d['year'] = m.group(2).strip()
    m = DA_SEARCH(ris_text)
    if m:
        if m.group(2):
            d['month'] = m.group(2).strip()
    m = SN_SEARCH(ris_text)
    if m:
        d['isbn'] = m.group(1).strip()
    # DOIs may be in N1 (notes) tag, search for it in any tag
    m = DOI_SEARCH(ris_text)
    if m:
        d['doi'] = m.group(0).strip()
    m = SP_SEARCH(ris_text)
    if m:
        d['startpage'] = m.group(1).strip()
        d['pages'] = d['startpage']
    m = EP_SEARCH(ris_text)
    if m:
        d['endpage'] = m.group(1).strip()
        d['pages'] = d['startpage'] + '–' + d['endpage']
    m = UR_SEARCH(ris_text)
    if m:
        # in IRS, url can be seprated using a ";"
        d['url'] = m.group(1).split(';')[0].strip()
    m = LA_SEARCH(ris_text)
    if m:
        d['language'] = m.group(1).strip()
    return d
