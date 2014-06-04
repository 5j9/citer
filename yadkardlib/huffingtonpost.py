#! /data/project/yadkard/venv/bin python
# -*- coding: utf-8 -*-

'''Contains codes specifically related to The Huffington Post website.'''

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
    
    '''Create the huffingtonpost citation object.'''
    
    def __init__(self, huffingtonpost_url):
        self.url = huffingtonpost_url
        self.dictionary = url2dictionary(huffingtonpost_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(huffingtonpost_url):
    '''Get huffingtonpost_url and return the result as a dictionary.'''
    r = requests.get(huffingtonpost_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code = ', r.status_code, ' != 200'
        return
    else:
        d = {}
        d['url'] = huffingtonpost_url
        d['type'] = 'web'
        d['website'] = 'The Huffington Post'
        bs = BS(r.text)
        m = bs.title
        if m:
            d['title'] = m.text.split('|')[0].strip()
        m = bs.find(attrs={'class':'author vcard'})
        if m:
            fullname = m.text
        if not m:
            m = bs.find(attrs={'class':'bold color_1A1A1A'})
            if m:
                fullname = m.text
        if not m:
            m = bs.find(attrs={'name':'author'})
            if m:
                fullname = m['content']
        if m:
            if fullname.startswith('By '):
                fullname = fullname[3:]
            d['authors'] = []
            d['authors'].append(conv.Name(fullname))
        m = re.search('(\d\d\d\d)\-(\d\d)\-(\d\d)',r.text)
        if m:
            d['date'] = m.group(0)
            d['year'] = m.group(1)
    return d


