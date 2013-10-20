#! /usr/bin/env python
# -*- coding: utf-8 -*-

#todo: editor and author and ... article link

import convertors as conv
from datetime import date

def create(d):
    '''Creates citation based on the given dictionary'''   
    if d['type'].lower() == 'book':
        s = '* {{یادکرد کتاب'
        if 'authors' in d:
            s += names2para(d['authors'],
                              'نام',
                              'نام خانوادگی'
                              )             
        if 'editors' in d:
            s += names2para(d['editors'],
                              'نام ویراستار',
                              'نام خانوادگی ویراستار'
                              )
        if 'translators' in d:
            s += translators2para(d['translators'])
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
        if 'month' in d:
            s += '|ماه=' + d['month']
        if 'isbn' in d:
            s += '|شابک=' + d['isbn']
        if 'url' in d:
            s += '|پیوند=' + d['url']
        if 'doi' in d:
            s += '|doi=' + d['doi']
        if 'language' in d:
            s += '|زبان=' + d['language']
        s += '|تاریخ بازبینی=' + date.isoformat(date.today())
        s += '}}'
        return s
    elif d['type'].lower() == 'article' or d['type'] == 'JOUR':
        s = '* {{یادکرد ژورنال'
        if 'authors' in d:
            s += names2para(d['authors'],
                              'نام',
                              'نام خانوادگی'
                              )
        if 'editors' in d:
            s += names2para(d['editors'],
                              'نام ویراستار',
                              'نام خانوادگی ویراستار'
                              )
        if 'translators' in d:
            s += translators2para(d['translators'])
        if 'title' in d:
            s += '|عنوان=' +  d['title']
        if 'journal' in d:
            s += '|ژورنال=' + d['journal']
        if 'year' in d:
            s += '|سال=' + d['year']
        if 'month' in d:
            s += '|ماه=' + d['month']
        if 'number' in d:
            s += '|شماره=' + d['number']
        if 'pages' in d:
            s += '|صفحه=' + d['pages']
        if 'url' in d:
            s += '|پیوند=' + d['url']
        if 'doi' in d:
            s += '|doi=' + d['doi']
        if 'language' in d:
            s += '|زبان=' + d['language']
        s += '|تاریخ بازبینی=' + date.isoformat(date.today())
        s += '}}'
        return s
    else:
        raise KeyError, d['type'] + " is not a defined condition for d['type']"

def names2para(names, fn_parameter, ln_parameter):
    '''takes lists of firstnames and lastnames and returns the string to be
appended to citation string'''
    c = 0
    s = ''
    for name in names:
        c += 1
        if c == 1:
            s += '|' + ln_parameter + '=' + name.lastname
            s += '|' + fn_parameter + '=' + name.firstname
        else:
            s += '|' + ln_parameter + conv.ennum2fa(c) + '=' +\
                 name.lastname
            s += '|' + fn_parameter + conv.ennum2fa(c) + '=' +\
                 name.firstname
    return s
            
def translators2para(translators):
    s = '|ترجمه='
    c = 0
    for name in translators:
        c += 1
        if c == 1:
            s += name.fullname
        elif c == len(names):
            s += ' و ' + name.fullname
        else:
            s += '، ' + name.fullname
    return s
        
