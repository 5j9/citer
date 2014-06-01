#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to New York Times website'''

import re
import requests

import langid

import conv
import isbn
import config

if config.lang == 'en':
    import wikiref_en as wikiref
    import wikicite_en as wikicite
else:
    import wikiref_fa as wikiref
    import wikicite_fa  as wikicite

class NYT():
    '''Creates an NYT object'''
    
    def __init__(self, nyt_url):
        self.url = nyt_url
        self.dictionary = url2dictionary(nyt_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(nyt_url):
    '''This is a parser function. Get nyt_url and returns a dict'''
    r = requests.get(nyt_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code != 200'
        return
    else:
        d = {}
        d['url'] = nyt_url
        d['type'] = 'web'
        d['website'] = 'The New York Times'
        pattern = r'<meta +name="hdl" +content="(.+)"'
        m = re.search(pattern, r.text)
        if m:
            d['title'] = m.group(1)
        pattern = r'<meta +name="byl" +content="(.+)"'
        m = re.search(pattern, r.text)
        if m:
            fullnames = m.group(1)
            if fullnames.startswith('By '):
                fullnames = fullnames[3:].split(' and ')
            else:
                fullnames = fullnames.split(' and ')
            d['authors'] = []
            for fullname in fullnames:
                d['authors'].append(conv.Name(fullname))
        pattern = r'<meta +name="pg" +content="(.+)"'
        m = re.search(pattern, r.text)
        if m:
            d['page'] = m.group(1)
        pattern = r'"(\d\d\d\d)(\d\d)(\d\d)"'
        m = re.search(pattern, r.text)
        if m:
            d['date'] = '-'.join(m.groups())
            d['year'] = m.group(1)          
    return d


