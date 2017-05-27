#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Define related tools for web.archive.org (aka Wayback Machine)."""

import re
import logging
from threading import Thread
from multiprocessing import Process, Pipe
from datetime import date
from urllib.parse import urlparse

from requests import ConnectionError as RequestsConnectionError

from commons import dictionary_to_response, Response
from urls import (
    urls_response, url2dict, get_hometitle, get_soup, find_authors,
    find_journal, find_site_name, find_title, ContentTypeError,
    ContentLengthError, StatusCodeError
)


URL_FULLMATCH = re.compile(
    r'https?://web(?:-beta)?\.archive\.org/(?:web/)?'
    r'(\d{4})(\d{2})(\d{2})\d{6}(?:id_|js_|cs_|im_)?/(http.*)'
).fullmatch


def waybackmachine_response(archive_url: str, date_format: str= '%Y-%m-%d'):
    """Create the response namedtuple."""
    m = URL_FULLMATCH(archive_url)
    if not m:
        # Could not parse the archive_url. Treat as an ordinary URL.
        return urls_response(archive_url, date_format)
    archive_year, archive_month, archive_day, original_url = \
        m.groups()
    parent_conn, child_conn = Pipe()
    original_process = Process(
        target=original_url2dict, args=(original_url, child_conn)
    )
    original_process.start()
    try:
        archive_dict = url2dict(archive_url)
    except (ContentTypeError, ContentLengthError) as e:
        logger.exception(archive_url)
        return Response(
            sfnt='Could not process the request.', ctnt=e, error=100
        )
    archive_dict['date_format'] = date_format
    archive_dict['url'] = original_url
    archive_dict['archive-url'] = archive_url
    archive_dict['archive-date'] = date(
        int(archive_year), int(archive_month), int(archive_day)
    )
    original_dict = parent_conn.recv()
    original_process.join()
    if original_dict:
        # The original_process has been successful
        if (
            original_dict['title'] == archive_dict['title']
            or original_dict['soup_title'] == archive_dict['soup_title']
        ):
            archive_dict.update(original_dict)
            archive_dict['dead-url'] = 'no'
        else:
            # and original title is the same as archive title. Otherwise it
            # means that the content probably has changed and the original data
            # cannot be trusted.
            archive_dict['dead-url'] = 'unfit'
    else:
        archive_dict['dead-url'] = 'yes'
    if archive_dict['website'] == 'Wayback Machine':
        archive_dict['website'] = (
            urlparse(original_url).hostname.replace('www.', '')
        )
    return dictionary_to_response(archive_dict)


def original_url2dict(ogurl: str, child_conn) -> None:
    """Fill the dictionary with the information found in ogurl."""
    try:
        original_dict = original_url_dict(ogurl)
    except (
        ContentTypeError,
        ContentLengthError,
        StatusCodeError,
        RequestsConnectionError,
    ):
        child_conn.send(None)
    except Exception:
        logger.exception(
            'There was an unexpected error in waybackmechine thread'
        )
        child_conn.send(None)
    else:
        child_conn.send(original_dict)


def original_url_dict(url: str):
    """Retuan dictionary only containng required data for og:url."""
    # Creating a thread to fetch homepage title in background
    hometitle_list = []  # A mutable variable used to get the thread result
    home_title_thread = Thread(
        target=get_hometitle, args=(url, hometitle_list)
    )
    home_title_thread.start()
    soup, html = get_soup(url)
    d = {'soup_title': soup.title.text.strip()}
    authors = find_authors(soup)
    if authors:
        d['authors'] = authors
    d['journal'] = find_journal(html)
    if d['journal']:
        d['cite_type'] = 'journal'
    else:
        d['cite_type'] = 'web'
        d['website'] = find_site_name(
            soup, url, authors, hometitle_list, home_title_thread
        )
    d['title'] = find_title(
        html, url, authors, hometitle_list, home_title_thread
    )
    return d


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("langid").setLevel(logging.WARNING)
    logger = logging.getLogger()
else:
    logger = logging.getLogger(__name__)
