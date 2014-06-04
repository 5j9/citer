#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This module contains codes specifically related to BBC news website.'''

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

class Citation():
    '''Create BBC citation object.'''
    
    def __init__(self, bbc_url):
        self.url = bbc_url
        self.dictionary = url2dictionary(bbc_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(bbc_url):
    '''Get bbc_url and return the result as a dictionary.'''
    r = requests.get(bbc_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code = ', r.status_code, ' != 200'
        return
    else:
        d = {}
        d['url'] = bbc_url
        d['type'] = 'web'
        d['website'] = 'BBC'
        bs = BS(r.text)
        if bs.h1:
            d['title'] = bs.h1.text
        else:
            m = bs.find('meta', attrs={'name':'Headline'})
            if m:
                 d['title'] = m['content']
        m = bs.find(attrs={'class':'byline'})
        if m:
            m = m.find(attrs={'class':'name'})
        if not m:
            m = bs.find(attrs={'class':'byline-name'})
        if not m:
            m = bs.find(attrs={'class':'byl'})
        if not m:
            m = bs.find(attrs={'class':'bylineAuthor'})
        if m:
            fullnames = m.text.strip()
            if fullnames.startswith('By '):
                fullnames = fullnames[3:]
            fullnames = fullnames.split(' and ')
            d['authors'] = []
            for fullname in fullnames:
                d['authors'].append(conv.Name(fullname))
        m = re.search('data-seconds="(.*?)"', r.text)
        if m:
            t = time.gmtime(int(m.group(1)))
            d['date'] = time.strftime('%Y-%m-%d', t)
            d['year'] = str(t.tm_year)
        else:
            m = bs.find(attrs={'name':'OriginalPublicationDate'})
            if m:
                d['date'] = m['content'][:10].replace('/','-')
                d['year'] = m['content'][:4]
    return d


