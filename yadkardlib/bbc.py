#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This module contains codes specifically related to BBC news website'''

import re
import time

import requests
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

class BBC():
    '''Creates an BBC object'''
    
    def __init__(self, bbc_url):
        self.url = bbc_url
        self.dictionary = url2dictionary(bbc_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(bbc_url):
    '''This is the page parser function. Gets bbc_url and returns the result as
a dictionary.'''
    r = requests.get(bbc_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code != 200'
        return
    else:
        d = {}
        d['url'] = bbc_url
        d['type'] = 'web'
        d['website'] = 'BBC'
        bs = BS(r.text)
        if bs.h1:
            d['title'] = bs.h1.text
        if bs.find('span', class_='name'):
            fullnames = bs.find('span', class_='name').text
            if fullnames.startswith('By '):
                fullnames = fullnames[3:]
            fullnames = fullnames.split(' and ')
            d['authors'] = []
            for fullname in fullnames:
                d['authors'].append(conv.Name(fullname))
        m = bs.find('p', class_=re.compile('.*date.*'))
        if m:
            t = time.gmtime(int(m['data-seconds']))
            d['date'] = time.strftime('%Y-%m-%d', t)
            d['year'] = str(t.tm_year)      
    return d


