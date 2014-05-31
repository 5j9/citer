#! /usr/bin/env python
# -*- coding: utf-8 -*-

#todo: editor and author and ... article link

from datetime import date

import wikiref_en as wikiref

def create(d):
    '''Creates citation based on the given dictionary'''   
    if d['type'] == 'book':
        s = '* {{cite book'
    elif d['type'] == 'article' or d['type'] == 'jour':
        s = '* {{cite journal'
    elif d['type'] == 'web':
        s = '* {{cite web'
    else:
        raise KeyError, d['type'] + " is not a defined condition for d['type']"

    if 'authors' in d:
        s += names2para(d['authors'],
                          'first',
                          'last'
                          )
    if 'editors' in d:
        s += names2para(d['editors'],
                          'editor-first',
                          'editor-last'
                          )
    if 'translators' in d:
        for translator in d['translators']:
            translator.fullname += u' (مترجم)'
        #todo: add a 'Translated by ' before name of translators
        if 'others' in d:
            d['others'].extend(d['translators'])
        else:
            d['others'] = d['translators']
    if 'others' in d:
        s += names1para(d['others'], 'others')
    if 'title' in d:
            s += '|title=' +  d['title']
    if 'journal' in d:
        s += '|journal=' + d['journal']
    if 'publisher' in d:
        s += '|publisher=' + d['publisher']
    if 'website' in d:
        s += '|website=' + d['website']
    if 'series' in d:
        s += '|series=' + d['series']
    if 'volume' in d:
        s += '|volume=' + d['volume']
    if 'number' in d:
        s += '|issue=' + d['number']
    if 'date' in d:
        s += '|date=' + d['date']
    if 'year' in d:
        s += '|year=' + d['year']
    if 'isbn' in d:
        s += '|isbn=' + d['isbn']
    if d['type'] == 'article' or d['type'] == 'jour':
        if 'pages' in d:
            if u'–' in d['pages']:
                s += '|pages=' + d['pages']
            else:
                s += '|page=' + d['pages']
    if 'url' in d:
        s += '|url=' + d['url']
    if 'doi' in d:
        s += '|doi=' + d['doi']
##    if 'language' in d:
##        if d['language'] not in 'Englishenglish'
##            s += '|language=' + d['language']
    if 'authors' in d:
        s += '|ref=harv'
    else:
        s += '|ref={{sfnref|' +\
             #order should be matched with wikiref
             d['publisher'] if 'publisher' in d else \
               d['journal'] if 'journal' in d else \
               d['website'] if 'website' in d else \
               d['title'] or 'Anon.' +\
             '|' + d['year'] + '}}'
    s += '|accessdate=' + date.isoformat(date.today())
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
            s += '|' + ln_parameter + str(c) + '=' +\
                 name.lastname
            s += '|' + fn_parameter + str(c) + '=' +\
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
            s += ', and ' + name.fullname
        else:
            s += ', ' + name.fullname
    return s
        
