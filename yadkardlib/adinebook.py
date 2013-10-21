#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''All things that are specifically related to adinebook website'''

import re
import urllib2

import langid

import fawikiref
import fawikicite
import conv
import isbn

class AdineBook():
    '''Creates a google book object'''
    
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
        self.ref =fawikiref.create(self.dictionary)
        self.cite = fawikicite.create(self.dictionary)

def isbn2url(isbn):
    #apparently adinebook uses 10 digit codes (without hyphens) for its books
    #if it's an isbn13 then the first 3 digits are excluded:
    isbn = isbn.replace('-', '')
    isbn = isbn.replace(' ', '')
    isbn = isbn.replace('-', '')
    if len(isbn) == 13:
        isbn = isbn [3:]
    url = 'http://www.adinebook.com/gp/product/' + isbn
    return url

def url2dictionary(adinebook_url):
    '''This is a parser function. Get adinebook_url and returns a dict'''
    try:
        adinebook_html = urllib2.urlopen(adinebook_url).read()
    except:
        #todo: log
        return
    if 'صفحه مورد نظر پبدا نشد.' in adinebook_html:
        return
    else:
        d = {}
        d['type'] = 'book'
        pattern = '<title>آدینه بوک:\s?(?P<title>.*?)\s?' +\
                '~(?P<names>.*?)\s?</title>'
        m = re.search(pattern, adinebook_html)
        if m:
            d['title'] = m.group('title')
        else:
            return
        names = m.group('names').split('،')
        #initiating name lists:
        if m.group('names'):
            d['authors'] = []
        if '(ويراستار)' in m.group('names'):
            d['editors'] = []
        if '(مترجم)' in m.group('names'):
            d['translators'] = []
        #building lists:
        for name in names:
            if '(ويراستار)' in name:
                d['editors'].append(conv.Name(
                                name.split('(ويراستار)')[0]
                                ))
            elif '(مترجم)' in name:
                d['translators'].append(conv.Name(
                                    name.split('(مترجم)')[0]
                                    ))
            elif '(' in name:
                #others are not important for wiki citation
                pass
            else:
                d['authors'].append(conv.Name(
                                name
                                ))
        m = re.search('نشر:</b>\s*(.*?)\s*\(.*</li>', adinebook_html)
        if m:
            d['publisher'] = m.group(1)
        m = re.search('نشر:</b>.*\([\d\s]*(.*?)،.*', adinebook_html)
        if m:
            d['month'] = m.group(1)
        m = re.search('نشر:</b>.*?\(.*?(\d\d\d\d)\)</li>', adinebook_html)
        if m:
            d['year'] = m.group(1)
        m = re.search('شابک:.*?([\d-]*)</span></li>', adinebook_html)
        if m:
            d['isbn'] = m.group(1)          
    return d


