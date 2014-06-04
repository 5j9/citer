#! /data/project/yadkard/venv/bin
# -*- coding: utf-8 -*-

'''Codes specifically related to the dailymail website.'''

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
    
    '''Create the DailyMail citation object.'''
    
    def __init__(self, dailymail_url):
        self.url = dailymail_url
        self.dictionary = url2dictionary(dailymail_url)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)
        self.error = 0


def url2dictionary(dailymail_url):
    '''Get dailymail_url and returns the result as a dictionary.'''
    r = requests.get(dailymail_url)
    if r.status_code != 200:
        #not OK. Probably 404
        print 'status_code = ', r.status_code, ' != 200'
        return
    else:
        d = {}
        d['url'] = dailymail_url
        d['type'] = 'web'
        d['website'] = 'Daily Mail'
        bs = BS(r.text)
        m = bs.find('meta', attrs={'property':'og:title'})
        if m:
            d['title'] = m['content']
        m = bs.findAll(attrs={'class':'author'})
        if m:
            d['authors'] = []
            for fullname in m:
                fullname = fullname.text
                if 'Reporter' in fullname:
                    name = conv.Name(fullname)
                    name.lastname = name.fullname
                    name.firstname = ''
                    d['authors'].append(name)
                else:
                    d['authors'].append(conv.Name(fullname))
        m = bs.find(attrs={'property':'article:modified_time'})
        if m:
            d['date'] = m['content'][:10]
            d['year'] = m['content'][:4]
    return d
