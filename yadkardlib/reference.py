#! /usr/bin/env python
# -*- coding: utf-8 -*-

def create(d):
    '''Creates citation based on the given dictionary'''
    if 'lastnames' in d:
        s = '<ref>{{پک'
        for lastname in d['lastnames']:
            s += '|' + lastname
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
