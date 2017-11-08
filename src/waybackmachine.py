#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Define related tools for web.archive.org (aka Wayback Machine)."""

import re
import logging
from threading import Thread
from datetime import date
from urllib.parse import urlparse

from requests import ConnectionError as RequestsConnectionError

from src.commons import dict_to_sfn_cit_ref
from src.urls import (
    urls_sfn_cit_ref, url2dict, get_home_title, get_html, find_authors,
    find_journal, find_site_name, find_title, ContentTypeError,
    ContentLengthError, StatusCodeError, TITLE_TAG
)


URL_FULLMATCH = re.compile(
    r'https?://web(?:-beta)?\.archive\.org/(?:web/)?'
    r'(\d{4})(\d{2})(\d{2})\d{6}(?:id_|js_|cs_|im_)?/(http.*)'
).fullmatch


def waybackmachine_sfn_cit_ref(
    archive_url: str, date_format: str= '%Y-%m-%d'
) -> tuple:
    """Create the response namedtuple."""
    m = URL_FULLMATCH(archive_url)
    if not m:
        # Could not parse the archive_url. Treat as an ordinary URL.
        return urls_sfn_cit_ref(archive_url, date_format)
    archive_year, archive_month, archive_day, original_url = \
        m.groups()
    original_dict = {}
    thread = Thread(
        target=original_url2dict, args=(original_url, original_dict)
    )
    thread.start()
    try:
        archive_dict = url2dict(archive_url)
    except (ContentTypeError, ContentLengthError) as e:
        logger.exception(archive_url)
        # Todo: i18n
        return 'Invalid content type or length.', e, ''
    archive_dict['date_format'] = date_format
    archive_dict['url'] = original_url
    archive_dict['archive-url'] = archive_url
    archive_dict['archive-date'] = date(
        int(archive_year), int(archive_month), int(archive_day)
    )
    thread.join()
    if original_dict:
        # The original_process has been successful
        if (
            original_dict['title'] == archive_dict['title']
            or original_dict['html_title'] == archive_dict['html_title']
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
    return dict_to_sfn_cit_ref(archive_dict)


def original_url2dict(ogurl: str, original_dict) -> None:
    """Fill the dictionary with the information found in ogurl."""
    # noinspection PyBroadException
    try:
        original_dict.update(original_url_dict(ogurl))
    except (
        ContentTypeError,
        ContentLengthError,
        StatusCodeError,
        RequestsConnectionError,
    ):
        pass
    except Exception:
        logger.exception(
            'There was an unexpected error in waybackmechine thread'
        )


def original_url_dict(url: str):
    """Retuan dictionary only containing required data for og:url."""
    d = {}
    # Creating a thread to fetch homepage title in background
    hometitle_list = []  # A mutable variable used to get the thread result
    home_title_thread = Thread(
        target=get_home_title, args=(url, hometitle_list)
    )
    home_title_thread.start()
    html = get_html(url)
    m = TITLE_TAG(html)
    html_title = m['result'] if m else None
    if html_title:
        d['html_title'] = html_title
    authors = find_authors(html)
    if authors:
        d['authors'] = authors
    journal = find_journal(html)
    if journal:
        d['journal'] = journal
        d['cite_type'] = 'journal'
    else:
        d['cite_type'] = 'web'
        d['website'] = find_site_name(
            html, html_title, url, authors, hometitle_list, home_title_thread
        )
    d['title'] = find_title(
        html, html_title, url, authors, hometitle_list, home_title_thread
    )
    return d


logger = logging.getLogger(__name__)
