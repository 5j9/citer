#! /usr/bin/env python
# -*- coding: utf-8 -*-

def create(d):
    '''Creates citation based on the given dictionary'''
    if 'authors' in d:
        s = '<ref>{{پک'
        c = 0
        for name in d['authors']:
            c += 1
            if c < 5: #{{پک}} only accepts a maximum of four authors
                s += '|' + name.lastname
    else:
        s = '<ref>{{پک/بن'
    if 'year' in d:
        s += '|' + d['year']
    if 'title' in d:
        s += '|ک=' + d['title']
    if 'language' in d:
        s += '|زبان=' + d['language']
    s += '|ص='
    if 'pages' in d:
        s += d['pages']
    s += '}}</ref>'
    return s
