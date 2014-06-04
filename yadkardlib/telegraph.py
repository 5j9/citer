#! /data/project/yadkard/venv/bin
# -*- coding: utf-8 -*-

'''Codes specifically related to the Daily Telegraph website.'''

import re
import time


import requests
try:
    from bs4 import BeautifulSoup as BS

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

class Citation():
    
    '''Create the telegraph citation object uring it's url.'''
    
    def __init__(self, telegraph_url):
        self.url = telegraph_url
        self.dictionary = url2dictionary(telegraph_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(telegraph_url):
    '''Get telegraph_url and returns the result as a dictionary.'''
    r = requests.get(telegraph_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code = ', r.status_code, ' != 200'
        return
    else:
        d = {}
        d['url'] = telegraph_url
        d['type'] = 'web'
        d['website'] = 'The Daily Telegraph'
        bs = BS(r.text)
        m = bs.h1
        if m:
            d['title'] = m.text.strip()
        m = bs.find(attrs={'name':'DCSext.author'})
        if m:
            fullname = m['content']
            if fullname.startswith('By '):
                fullname = fullname[3:]
            if ',' in fullname:
                fullname = fullname.split(',')[0]
            if ' in ' in fullname:
                fullname = fullname.split(' in ')[0]
            d['authors'] = []
            d['authors'].append(conv.Name(fullname))
        m = bs.find(attrs={'name':'last-modified'})
        if m:
            d['date'] = m['content'][:10]
            d['year'] = m['content'][:4]
    return d


