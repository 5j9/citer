#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This module contains codes specifically related to mirror website'''

import re
import time


import requests
try:
    from bs4 import BeautifulSoup as BS
except ImportError:
    from BeautifulSoup import BeautifulSoup as BS
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

class DM():
    '''Creates an mirror object'''
    
    def __init__(self, mirror_url):
        self.url = mirror_url
        self.dictionary = url2dictionary(mirror_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(mirror_url):
    '''This is the page parser function. Gets mirror_url and returns the
result as a dictionary.'''
    r = requests.get(mirror_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code = ', r.status_code, ' != 200'
        return
    else:
        d = {}
        d['url'] = mirror_url
        d['type'] = 'web'
        d['website'] = 'Daily Mirror'
        bs = BS(r.text)
        m = bs.h1
        if m:
            d['title'] = m.text.strip()
        m = bs.find('meta', attrs={'name':'author'})
        if m:
            d['authors'] = []
            fullname = m['content']
            if fullname != 'mirror Administrator':
                d['authors'].append(conv.Name(fullname))
            else:
               del d['authors']
        m = bs.find(attrs={'property':'article:published_time'})
        if m:
            d['date'] = m['content'][:10]
            d['year'] = m['content'][:4]
    return d


