#! /data/project/yadkard/venv/bin python
# -*- coding: utf-8 -*-

'''All things that are specifically related to adinebook website'''

import re
import urllib2

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
    '''Create Adinebook citation object.'''
    
    def __init__(self, adinebook_url):
        self.url = adinebook_url
        self.dictionary = url2dictionary(adinebook_url)
        #manually adding page nubmer to dictionary:
        if 'language' in self.dictionary:
            self.error = 0
        else:
            #assume that language is either fa or en
            #todo: give warning about this
            langid.set_languages(['en','fa'])
            self.dictionary['language'], confidence =\
                                     langid.classify(self.dictionary['title'])
            self.error = round((1 - confidence) * 100, 2)
        self.ref = wikiref.create(self.dictionary)
        self.cite = wikicite.create(self.dictionary)


def isbn2url(isbn):
    '''Convert isbn string to AdinebookURL. Return the url as string.'''
    #apparently adinebook uses 10 digit codes (without hyphens) for its books
    #if it's an isbn13 then the first 3 digits are excluded:
    isbn = isbn.replace('-', '')
    isbn = isbn.replace(' ', '')
    if len(isbn) == 13:
        isbn = isbn [3:]
    url = 'http://www.adinebook.com/gp/product/' + isbn
    return url

def url2dictionary(adinebook_url):
    '''Get adinebook_url and return the result as a dict.'''
    try:
        #this try statement is needed because if adinebook is not available then
        #    ottobib should continoue its' work in isbn.py
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent',
                              'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0)' +
                              ' Gecko/20100101 Firefox/24.0')]
        adinebook_html = opener.open(adinebook_url).read().decode('utf8')
    except:
        #todo: log
        return
    if u'صفحه مورد نظر پبدا نشد.' in adinebook_html:
        return
    else:
        d = {}
        d['type'] = 'book'
        pattern = u'<title>آدینه بوک:\s?(?P<title>.*?)\s?' +\
                '~(?P<names>.*?)\s?</title>'
        m = re.search(pattern, adinebook_html)
        if m:
            d['title'] = m.group('title')
        else:
            return
        names = m.group('names').split(u'،')
        #initiating name lists:
        if m.group('names'):
            d['authors'] = []
            d['others'] = []
        if u'(ويراستار)' in m.group('names'):
            d['editors'] = []
        if u'(مترجم)' in m.group('names'):
            d['translators'] = []
        #building lists:
        for name in names:
            if u'(ويراستار)' in name:
                d['editors'].append(conv.Name(
                                name.split(u'(ويراستار)')[0]
                                ))
            elif u'(مترجم)' in name:
                d['translators'].append(conv.Name(
                                    name.split(u'(مترجم)')[0]
                                    ))
            elif '(' in name:
                d['others'].append(conv.Name(
                                        re.split('\(.*\)', name)[0]
                                        ))
                d['others'][-1].fullname = name
            else:
                d['authors'].append(conv.Name(
                                name
                                ))
        if not d['authors']:
            del d['authors']
        if not d['others']:
            del d['others']
        m = re.search(u'نشر:</b>\s*(.*?)\s*\(.*</li>', adinebook_html)
        if m:
            d['publisher'] = m.group(1)
        m = re.search(u'نشر:</b>.*\([\d\s]*(.*?)،.*', adinebook_html)
        if m:
            d['month'] = m.group(1)
        m = re.search(u'نشر:</b>.*?\(.*?(\d\d\d\d)\)</li>', adinebook_html)
        if m:
            d['year'] = m.group(1)
        m = re.search(u'شابک:.*?([\d-]*)</span></li>', adinebook_html)
        if m:
            d['isbn'] = m.group(1)          
    return d
