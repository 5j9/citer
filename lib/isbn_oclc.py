from json import loads
from logging import getLogger
from threading import Thread
from typing import Optional

from isbnlib import info as isbn_info, mask as isbn_mask
from langid import classify
from regex import search

from config import LANG
from lib.citoid import get_citoid_dict
from lib.commons import (
    FOUR_DIGIT_NUM,
    ISBN10_SEARCH,
    ISBN13_SEARCH,
    ReturnError,
    request,
)
from lib.ketabir import (
    isbn_to_url as ketabir_isbn2url,
    url_to_dict as ketabir_url_to_dict,
)
from lib.urls import url_to_dict

RM_DASH_SPACE = str.maketrans('', '', '- ')


class IsbnError(Exception):

    """Raise when bibliographic information is not available."""

    pass


def isbn_to_dict(
    isbn_container_str: str,
    pure: bool = False,
    date_format: str = '%Y-%m-%d',
) -> dict:
    if pure:
        isbn = isbn_container_str
    else:
        # search for isbn13
        if (m := ISBN13_SEARCH(isbn_container_str)) is not None:
            isbn = m[0]
        else:
            # search for isbn10
            isbn = ISBN10_SEARCH(isbn_container_str)[0]

    if (iranian_isbn := isbn_info(isbn) == 'Iran') is True:
        ketabir_result_list = []
        ketabir_thread = Thread(
            target=ketabir_thread_target, args=(isbn, ketabir_result_list)
        )
        ketabir_thread.start()

    google_books_result = []
    google_books_thread = Thread(
        target=google_books,
        args=(isbn, google_books_result),
    )
    google_books_thread.start()

    citoid_result_list = []
    citoid_thread = Thread(
        target=citoid_thread_target, args=(isbn, citoid_result_list)
    )
    citoid_thread.start()

    citoid_thread.join()
    if citoid_result_list:
        dictionary = citoid_result_list[0]
    else:
        dictionary = {}

    google_books_thread.join()
    if google_books_result:
        dictionary.update(google_books_result[0])

    if iranian_isbn is True:
        # noinspection PyUnboundLocalVariable
        ketabir_thread.join()
        # noinspection PyUnboundLocalVariable
        if ketabir_result_list:
            # noinspection PyUnboundLocalVariable
            ketabir_dict = ketabir_result_list[0]
            dictionary = combine_dicts(ketabir_dict, dictionary)

    if not dictionary:
        raise ReturnError('Error: ISBN not found', '', '')

    dictionary['isbn'] = isbn_mask(isbn)
    dictionary['date_format'] = date_format
    if 'language' not in dictionary:
        dictionary['language'] = classify(dictionary['title'])[0]
    return dictionary


def ketabir_thread_target(isbn: str, result: list) -> None:
    # noinspection PyBroadException
    try:
        if (url := ketabir_isbn2url(isbn)) is None:
            return  # ketab.ir does not have any entries for this isbn
        if d := ketabir_url_to_dict(url):
            result.append(d)
    except Exception:
        logger.exception('isbn: %s', isbn)
        return


def combine_dicts(ketabir: dict, citoid: dict) -> dict:
    if not ketabir and not citoid:
        raise IsbnError('Bibliographic information not found.')

    if not ketabir:
        return citoid
    elif not citoid:
        return ketabir

    # both ketabid and citoid are available
    if LANG == 'fa':
        result = ketabir
        if (oclc := citoid['oclc']) is not None:
            result['oclc'] = oclc
        return result
    return citoid


def isbn2int(isbn):
    return int(isbn.translate(RM_DASH_SPACE))


def google_books(isbn: str, result: list):
    try:
        j = request(
            f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn.replace("-", "")}'
        ).json()
        d = j['items'][0]
        d.update(d['volumeInfo'])
    except Exception:  # noqa
        return
    if authors := d['authors']:
        d['authors'] = [a.rsplit(' ', 1) for a in authors]
    if date := d.get('publishedDate'):
        d['date'] = date
    d['cite_type'] = 'book'
    result.append(d)


def citoid_thread_target(isbn: str, result: list) -> None:
    try:
        d = get_citoid_dict(isbn)
    except Exception:
        return
    result.append(d)


def worldcat_url_to_dict(url: str, date_format: str = '%Y-%m-%d', /) -> dict:
    try:
        oclc = search(r'(?i)worldcat.org/(?:title|oclc)/(\d+)', url)[1]
    except TypeError:  # 'NoneType' object is not subscriptable
        # e.g. on https://www.worldcat.org/formats-editions/22239204
        return url_to_dict(url, date_format)
    return oclc_dict(oclc, date_format)


def oclc_dict(oclc: str, date_format: str = '%Y-%m-%d', /) -> dict:
    content = request('https://www.worldcat.org/title/' + oclc).content
    j = loads(
        content[
            (s := (f := content.find)(b' type="application/json">') + 25) : f(
                b'</script>', s
            )
        ]
    )
    record = j['props']['pageProps']['record']
    if record is None:  # invalid OCLC number
        raise ReturnError(
            'Error processing OCLC number: ' + oclc,
            'Make sure the OCLC identifier is valid.',
            '',
        )
    d = {}
    d['cite_type'] = record['generalFormat'].lower()
    d['title'] = record['title']
    d['authors'] = [
        ('', c['nonPersonName']['text'])
        if 'nonPersonName' in c
        else (c['firstName']['text'], c['secondName']['text'])
        for c in record['contributors']
    ]
    if (publisher := record['publisher']) != '[publisher not identified]':
        d['publisher'] = publisher
    if (
        place := record['publicationPlace']
    ) != '[Place of publication not identified]':
        d['publisher-location'] = place
    if m := FOUR_DIGIT_NUM(record['publicationDate']):
        d['year'] = m[0]
    d['language'] = record['catalogingLanguage']
    if isbn := record['isbn13']:
        d['isbn'] = isbn
    if issns := record['issns']:
        d['issn'] = issns[0]
    d['oclc'] = oclc
    d['date_format'] = date_format
    return d


logger = getLogger(__name__)
