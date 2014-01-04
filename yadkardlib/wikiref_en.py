#! /usr/bin/env python
# -*- coding: utf-8 -*-

def create(d):
    '''Creates citation based on the given dictionary'''
    s = '{{sfn'
    if 'authors' in d:
        c = 0
        for name in d['authors']:
            c += 1
            if c < 5: #{{sfn}} only supports a maximum of four authors
                s += '|' + name.lastname
    else:
        s += '|' + d['title']
    if 'year' in d:
        s += '|' + d['year']
    if 'pages' in d:
        if u'–' in d['pages']:
            s += '|pp=' + d['pages']
        else:
            s += '|p=' + d['pages']
    else:
        s += '|p='
    s += '}}'
    return s
