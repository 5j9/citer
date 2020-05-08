#! /usr/bin/python
# -*- coding: utf-8 -*-

"""All things specifically related to the Google Books website."""


from urllib.parse import parse_qs
from urllib.parse import urlparse

from langid import classify

from lib.commons import request
from lib.ris import parse as ris_parse
from lib.commons import dict_to_sfn_cit_ref


def googlebooks_sfn_cit_ref(url, date_format='%Y-%m-%d') -> tuple:
    """Create the response namedtuple."""
    parsed_url = urlparse(url)
    parsed_query = parse_qs(parsed_url.query)
    book_id = parsed_query["id"][0]
    dictionary = ris_parse(request(
        f'http://books.google.com/books/download/?id={book_id}'
        f'&output=ris', spoof=True).content.decode('utf8'))
    dictionary['date_format'] = date_format
    # default domain is prefered:
    dictionary['url'] = f'https://{parsed_url.netloc}/books?id={book_id}'
    # manually adding page number to dictionary:
    pg = parsed_query.get('pg')
    if pg is not None:
        pg0 = pg[0]
        dictionary['page'] = pg0[2:]
        dictionary['url'] += f'&pg={pg0}'
    # although google does not provide a language field:
    if not dictionary['language']:
        dictionary['language'] = classify(dictionary['title'])[0]
    return dict_to_sfn_cit_ref(dictionary)
