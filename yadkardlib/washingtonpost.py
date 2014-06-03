#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This module contains codes specifically related to washingtonpost website'''

import re
from datetime import datetime

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


class WP():
    '''Creates an washingtonpost's response object'''
    
    def __init__(self, washingtonpost_url):
        self.url = washingtonpost_url
        self.dictionary = url2dictionary(washingtonpost_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(washingtonpost_url):
    '''This is the page parser function. Gets washingtonpost_url and returns the
result as a dictionary.'''
    r = requests.get(washingtonpost_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code = ', r.status_code, ' != 200'
        return
    else:
        d = {}
        d['url'] = washingtonpost_url
        d['type'] = 'web'
        d['website'] = 'The Washingtonpost Post'
        bs = BS(r.text)
        #title:
        
        if bs.find(attrs={'name':'DC.title'}):
            d['title'] = bs.find(attrs={'name':'DC.title'})['content']
        elif bs.find(attrs={'property':'og:title'}):
            d['title'] = bs.find(attrs={'property':'og:title'})['content']
        elif bs.h1:
            d['title'] = bs.h1.text
        elif bs.title:
            if bs.title.text.endswith(' (washingtonpost.com)') or \
               bs.title.text.endswith(' - washingtonpost.com'):
                d['title'] = bs.title.text[:-21]
            else:
                d['title'] = bs.title.text
            d['title'] = d['title'].strip()
        #authors
        fullnames = None
        
        if bs.find(attrs={'class':'pb-byline'}):
            fullnames = bs.find(attrs={'class':'pb-byline'}).text
        elif bs.find(attrs={'id':'byline'}):
            fullnames = bs.find(attrs={'id':'byline'}).text
        elif bs.find(attrs={'name':'DC.creator'}):
            fullnames = bs.find(attrs={'name':'DC.creator'})['content']
        elif re.search('wp_author = "(.*?)";', r.text):
            fullnames = re.search('wp_author = "(.*)"', r.text).group(1)
        elif bs.find(attrs={'name':'reviewer'}):
            fullnames = bs.find(attrs={'name':'reviewer'})['content']
        elif bs.find(attrs={'size':'2'}):
            if bs.find(attrs={'size':'2'}).i:
                fullnames = bs.find(attrs={'size':'2'}).i.text
                
        if fullnames:
            if fullnames.startswith('By '):
                fullnames = fullnames[3:]
            fullnames = re.split(' and |, ', fullnames)
            d['authors'] = []
            for fullname in fullnames:
                d['authors'].append(conv.Name(fullname))
        #date
        m = bs.find(attrs={'name':'DC.date.issued'})
        if m:
            d['date'] = m['content']
            d['year'] = d['date'][:4]
        elif bs.find(attrs={'name':'pub_date'}):
            m = bs.find(attrs={'name':'pub_date'})['content']
            d['year'] = m[:4]
            d['date'] = m[:4] + '-' + \
                        m[4:6] + '-' + \
                        m[6:]
        elif bs.find(attrs={'property':'og:url'}):
            m = bs.find(attrs={'property':'og:url'})
            m = re.search('\d\d\d\d/\d\d/\d\d', m['content'])
            if not m:
                m = re.search('\d\d\d\d/\d\d/\d\d', washingtonpost_url)
            if m:
                d['date'] = m.group().replace('/', '-')
                d['year'] = d['date'][:4]
        elif bs.find(attrs={'class':"posted",'style':"line-height: 140%;"}):
            m = re.search(conv.en_month_pattern + ' \d\d, \d\d\d\d',
                          bs.find(attrs={'class':"posted",'style':
                                         "line-height: 140%;"}).text)
            if m:
                d['date'] = datetime.strptime(m.group(),
                                              '%B %d, %Y').strftime('%Y-%m-%d')
                d['year'] = d['date'][:4] 
    return d
