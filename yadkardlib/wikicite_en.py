#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

#todo: editor and author and ... article link


from datetime import date

import conv
import wikiref_en as wikiref


def create(d, date_format):
    """Create citation based on the given dictionary."""
    if d['type'] == 'book':
        s = '* {{cite book'
    elif d['type'] in ['article', 'jour']:
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
    elif 'website' in d:
        s += '|website=' + d['website']
    if 'publisher' in d:
        s += '|publisher=' + d['publisher']
    if 'address' in d:
        s += '|location=' + d['address']
    if 'series' in d:
        s += '|series=' + d['series']
    if 'volume' in d:
        s += '|volume=' + d['volume']
    if 'issue' in d:
        s += '|issue=' + d['issue']
    if 'date' in d:
        s += '|date=' + conv.chdateformat(d['date'], date_format)
    if 'year' in d:
        s += '|year=' + d['year']
    if 'isbn' in d:
        s += '|isbn=' + d['isbn']
    if 'issn' in d:
        s += '|issn=' + d['issn']
    if 'pmid' in d:
        s += '|pmid=' + d['pmid']
    if d['type'] in ['article', 'jour']:
        if 'pages' in d:
            if u'–' in d['pages']:
                s += '|pages=' + d['pages']
            else:
                s += '|page=' + d['pages']
    if 'url' in d:
        s += '|url=' + d['url']
    if 'doi' in d:
        s += '|doi=' + d['doi']
    if 'language' in d:
        if d['language'].lower() not in ['english','en']:
            s += '|language=' + d['language']
    if 'authors' in d:
        s += '|ref=harv'
    else:
        #order should be matched with wikiref
        s += '|ref={{sfnref|' +\
             (
                 d['publisher'] if 'publisher' in d else \
                 d['journal'] if 'journal' in d else \
                 d['website'] if 'website' in d else \
                 d['title'] if 'title' in d else \
                 'Anon.'
                 )
        if 'year' in d:
            s += '|' + d['year']
        s += '}}'
    if 'url' in d:
        s += '|accessdate=' + date.strftime(date.today(), date_format)
    s += '}}'
    return s


def names2para(names, fn_parameter, ln_parameter):
    """Take list of names. Return the string to be appended to citation."""
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
    """Take list of names. Return the string to be appended to citation."""
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
