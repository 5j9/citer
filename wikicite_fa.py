#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

#todo: editor and author and ... article link

from datetime import date

import commons

def create(d):
    """Creates citation based on the given dictionary"""   
    if d['type'] == 'book':
        s = '* {{یادکرد کتاب'
    elif d['type'] == 'article' or d['type'] == 'jour':
        s = '* {{یادکرد ژورنال'
    else:
        raise KeyError(d['type'] + " is not a defined condition for d['type']")

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
        s += names1para(d['translators'], 'ترجمه')
    if 'others' in d:
        s += names1para(d['others'], 'دیگران')
    if 'title' in d:
        if d['type'] == 'book':
            s += '|کتاب=' +  d['title']
        else:
            s += '|عنوان=' +  d['title']
    if 'journal' in d:
        s += '|ژورنال=' + d['journal']
    if 'publisher' in d:
        s += '|ناشر=' + d['publisher']
    if 'series' in d:
        s += '|سری=' + d['series']
    if 'volume' in d:
        s += '|جلد=' + d['volume']
    if 'issue' in d:
        s += '|شماره=' + d['issue']
    if 'year' in d:
        s += '|سال=' + d['year']
    if 'month' in d:
        s += '|ماه=' + d['month']
    if 'isbn' in d:
        s += '|شابک=' + d['isbn']
    if d['type'] == 'article' or d['type'] == 'jour':
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
            s += '|' + ln_parameter + commons.ennum2fa(c) + '=' +\
                 name.lastname
            s += '|' + fn_parameter + commons.ennum2fa(c) + '=' +\
                 name.firstname
    return s
            
def names1para(translators, para):
    s = '|' + para + '='
    c = 0
    for name in translators:
        c += 1
        if c == 1:
            s += name.fullname
        elif c == len(translators):
            s += ' و ' + name.fullname
        else:
            s += '، ' + name.fullname
    return s
        
