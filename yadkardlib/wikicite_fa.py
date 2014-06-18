#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

#todo: editor and author and ... article link

from datetime import date

import conv

def create(d):
    """Creates citation based on the given dictionary"""   
    if d['type'] == 'book':
        s = u'* {{یادکرد کتاب'
    elif d['type'] == 'article' or d['type'] == 'jour':
        s = u'* {{یادکرد ژورنال'
    else:
        raise KeyError, d['type'] + " is not a defined condition for d['type']"

    if 'authors' in d:
        s += names2para(d['authors'],
                          u'نام',
                          u'نام خانوادگی'
                          )             
    if 'editors' in d:
        s += names2para(d['editors'],
                          u'نام ویراستار',
                          u'نام خانوادگی ویراستار'
                          )
    if 'translators' in d:
        s += names1para(d['translators'], u'ترجمه')
    if 'others' in d:
        s += names1para(d['others'], u'دیگران')
    if 'title' in d:
        if d['type'] == 'book':
            s += u'|کتاب=' +  d['title']
        else:
            s += u'|عنوان=' +  d['title']
    if 'journal' in d:
        s += u'|ژورنال=' + d['journal']
    if 'publisher' in d:
        s += u'|ناشر=' + d['publisher']
    if 'series' in d:
        s += u'|سری=' + d['series']
    if 'volume' in d:
        s += u'|جلد=' + d['volume']
    if 'issue' in d:
        s += u'|شماره=' + d['issue']
    if 'year' in d:
        s += u'|سال=' + d['year']
    if 'month' in d:
        s += u'|ماه=' + d['month']
    if 'isbn' in d:
        s += u'|شابک=' + d['isbn']
    if d['type'] == 'article' or d['type'] == 'jour':
        if 'pages' in d:
            s += u'|صفحه=' + d['pages']
    if 'url' in d:
        s += u'|پیوند=' + d['url']
    if 'doi' in d:
        s += '|doi=' + d['doi']
    if 'language' in d:
        s += u'|زبان=' + d['language']
    s += u'|تاریخ بازبینی=' + date.isoformat(date.today())
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
            s += '|' + ln_parameter + conv.ennum2fa(c) + '=' +\
                 name.lastname
            s += '|' + fn_parameter + conv.ennum2fa(c) + '=' +\
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
            s += u' و ' + name.fullname
        else:
            s += u'، ' + name.fullname
    return s
        
