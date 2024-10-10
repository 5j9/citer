#!/usr/bin/env python3

import argparse
import html

import app

def main():
    ap = argparse.ArgumentParser()
    types = list(app.input_type_to_resolver.keys())
    ap.add_argument('-t', '--type', choices=types, metavar='TYPE', default='url-doi-isbn', help=str.join(' or ', map(repr, types)))
    ap.add_argument('-d', '--date-format', metavar='DATE-FMT', default='%Y-%m-%d')
    ap.add_argument('ident', metavar='URL-OR-ID')
    options = ap.parse_args()
    resolver = app.input_type_to_resolver[options.type]
    d = resolver(options.ident, options.date_format)
    scr = app.dict_to_sfn_cit_ref(d)
    for item in scr:
        print(html.unescape(item), end='\n\n')

if __name__ == '__main__':
    main()
