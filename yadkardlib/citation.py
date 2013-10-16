#! /usr/bin/env python
# -*- coding: utf-8 -*-

import converter as conv
from datetime import date

def create(d):
    '''Creates citation based on the given dictionary'''   
    if d['type'].lower() == 'book':
        s = '* {{یادکرد کتاب'
        if 'lastnames' in d:
            c = 0
            for lastname in d['lastnames']:
                    c += 1
                    s += '|نام خانوادگی%s=' %conv.ennum2fa(c)
                    s += lastname
                    s += '|نام%s=' %conv.ennum2fa(c)
                    s += d['firstnames'][c-1]
        if 'title' in d:
            s += '|کتاب=' +  d['title']
        if 'publisher' in d:
            s += '|ناشر=' + d['publisher']
        if 'series' in d:
            s += '|سری=' + d['series']
        if 'volume' in d:
            s += '|جلد=' + d['volume']
        if 'year' in d:
            s += '|سال=' + d['year']
        if 'isbn' in d:
            s += '|شابک=' + d['isbn']
        if 'url' in d:
            s += '|پیوند=' + d['url']
        if 'language' in d:
            s += '|زبان=' + d['language']
        s += '|تاریخ بازبینی=' + date.isoformat(date.today())
        s += '}}'
        return s
    elif d['type'].lower == 'article' or d['type'] == 'JOUR':
        s = '* {{یادکرد ژورنال'
        if 'lastnames' in d:
            c = 0
            for lastname in d['lastnames']:
                    c += 1
                    s += '|نام خانوادگی%s=' %conv.ennum2fa(c)
                    s += lastname
                    s += '|نام%s=' %conv.ennum2fa(c)
                    s += d['firstnames'][c-1]
        if 'title' in d:
            s += '|عنوان=' +  d['title']
        if 'journal' in d:
            s += '|ژورنال=' + d['journal']
        if 'year' in d:
            s += '|سال=' + d['year']
        if 'number' in d:
            s += '|شماره=' + d['number']
        if 'pages' in d:
            s += '|صفحه=' + d['pages']
        if 'url' in d:
            s += '|پیوند=' + d['url']
        if 'language' in d:
            s += '|زبان=' + d['language']
        s += '|تاریخ بازبینی=' + date.isoformat(date.today())
        s += '}}'
        return s
    else:
        raise KeyError, d['type'] + " is not a defined condition for d['type']"
