from json import loads
from threading import Thread

from isbnlib import info as isbn_info, mask as isbn_mask
from langid import classify
from regex import search

from config import LANG
from lib import four_digit_num, logger
from lib.citoid import citoid_data
from lib.commons import (
    ReturnError,
    isbn10_search,
    isbn13_search,
    request,
)
from lib.ketabir import (
    isbn_to_url as ketabir_isbn2url,
    ketabir_data as ketabir_url_to_dict,
)
from lib.urls import url_data

RM_DASH_SPACE = str.maketrans('', '', '- ')


class IsbnError(Exception):
    """Raise when bibliographic information is not available."""

    pass


def isbn_data(
    isbn_container_str: str,
    pure: bool = False,
    date_format: str = '%Y-%m-%d',
) -> dict:
    if pure:
        isbn = isbn_container_str
    else:
        # search for isbn13
        if (m := isbn13_search(isbn_container_str)) is not None:
            isbn = m[0]
        else:
            # search for isbn10
            isbn = isbn10_search(isbn_container_str)[0]

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
        d = citoid_result_list[0]
    else:
        d = {}

    google_books_thread.join()
    if google_books_result:
        d |= google_books_result[0]

    if iranian_isbn is True:
        # noinspection PyUnboundLocalVariable
        ketabir_thread.join()
        # noinspection PyUnboundLocalVariable
        if ketabir_result_list:
            # noinspection PyUnboundLocalVariable
            ketabir_dict = ketabir_result_list[0]
            d = combine_dicts(ketabir_dict, d)

    if not d:
        raise ReturnError('Error: ISBN not found', '', '')

    d['isbn'] = isbn_mask(isbn)
    d['date_format'] = date_format
    if 'language' not in d:
        d['language'] = classify(d['title'])[0]
    return d


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
        d |= d['volumeInfo']
    except Exception:  # noqa
        # logger.exception('isbn: %s', isbn)
        return
    if authors := d['authors']:
        d['authors'] = [a.rsplit(' ', 1) for a in authors]
    if date := d.get('publishedDate'):
        d['date'] = date
    d['cite_type'] = 'book'
    result.append(d)


def citoid_thread_target(isbn: str, result: list) -> None:
    try:
        d = citoid_data(isbn)
    except Exception:
        return
    result.append(d)


def worldcat_data(url: str) -> dict:
    try:
        oclc = search(r'(?i)worldcat.org/(?:title|oclc)/(\d+)', url)[1]
    except TypeError:  # 'NoneType' object is not subscriptable
        # e.g. on https://www.worldcat.org/formats-editions/22239204
        return url_data(url)
    return oclc_data(oclc)


def oclc_data(oclc: str) -> dict:
    content = request('https://search.worldcat.org/title/' + oclc).content
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
    if m := four_digit_num(record['publicationDate']):
        d['year'] = m[0]
    d['language'] = record['catalogingLanguage']
    if isbn := record['isbn13']:
        d['isbn'] = isbn
    if issns := record['issns']:
        d['issn'] = issns[0]
    d['oclc'] = oclc
    return d
