#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

def create(d):
    """Creates citation based on the given dictionary"""
    s = '{{sfn'
    if 'authors' in d:
        c = 0
        for name in d['authors']:
            c += 1
            if c < 5: #{{sfn}} only supports a maximum of four authors
                s += '|' + name.lastname
    else:
        #the same order should be used in wikicite:
        s += '|' + (d['publisher'] if 'publisher' in d else \
                    d['journal'] if 'journal' in d else \
                    d['website'] if 'website' in d else \
                    d['title'] if 'title' in d else \
                    'Anon.')
    if 'year' in d:
        s += '|' + d['year']
    if 'pages' in d:
        if '–' in d['pages']:
            s += '|pp=' + d['pages']
        else:
            s += '|p=' + d['pages']
    elif not 'url' in d:
        s += '|p='
    s += '}}'
    return s
