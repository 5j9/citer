#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

'''Codes specifically related to the Boston Globe website.'''

import re
from datetime import datetime

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


class Citation():
    
    '''Create Boston Globe citation object.'''
    
    def __init__(self, boston_url):
        self.url = boston_url
        self.dictionary = url2dictionary(boston_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(boston_url):
    '''Get boston_url and return the result as a dictionary.'''
    r = requests.get(boston_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code = ', r.status_code, ' != 200'
        return
    else:
        d = {}
        d['url'] = boston_url
        d['type'] = 'web'
        d['website'] = 'The Boston Globe'
        bs = BS(r.text)
        #title:
        if bs.find(attrs={'class':'main-hed'}):
            d['title'] = bs.find(attrs={'class':'main-hed'}).text.strip()
        elif bs.find(attrs={'property':'og:title'}):
            m = bs.find(attrs={'property':'og:title'})['content']
            if m.endswith(' - The Boston Globe'):
                d['title'] = m[:-19].strip()
            else:
                d['title'] = m.strip()
        elif bs.h1:
            d['title'] = bs.h1.text.strip()
        #authors
        fullnames = None
        if bs.find(attrs={'class':'story-byline'}):
            fullnames = bs.find(attrs={'class':'story-byline'}).text
        elif bs.find(attrs={'class':'author'}):
            fullnames = bs.find(attrs={'class':'author'}).text
                
        if fullnames:
            fullnames = fullnames.strip()
            if fullnames.startswith('By '):
                fullnames = fullnames[3:]
            fullnames = re.split(' and |, ', fullnames)
            d['authors'] = []
            for fullname in fullnames:
                d['authors'].append(conv.Name(fullname))
        #date
        m = bs.find(attrs={'name':'publish-date'})
        if m:
            m = datetime.strptime(m['content'], '%a, %d %b %Y %H:%M:%S EDT')
            d['date'] = m.strftime('%Y-%m-%d')
            d['year'] = d['date'][:4]
        elif bs.find(attrs={'class':'byline'}):
            m = conv.finddate(bs.find(attrs={'class':'byline'}).text)
            if m:
                d['date'] = m.strftime('%Y-%m-%d')
                d['year'] = d['date'][:4] 
    return d