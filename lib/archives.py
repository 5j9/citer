from datetime import date
from threading import Thread
from urllib.parse import urlparse

from curl_cffi import CurlError

from lib import logger
from lib.commons import rc
from lib.urls import (
    TITLE_TAG,
    ContentLengthError,
    ContentTypeError,
    analyze_home,
    find_authors,
    find_journal,
    find_site_name,
    find_title,
    get_html,
    url_data,
    url_to_dict as urls_url_to_dict,
)

URL_FULLMATCH = rc(
    r'https?+://web(?:-beta)?+\.archive\.org/(?:web/)?+'
    r'(\d{4})(\d{2})(\d{2})\d{6}(?>cs_|i(?>d_|m_)|js_)?+/(http.*)'
).fullmatch


def url_to_dict(archive_url: str, date_format: str = '%Y-%m-%d') -> dict:
    if (m := URL_FULLMATCH(archive_url)) is None:
        # Could not parse the archive_url. Treat as an ordinary URL.
        return urls_url_to_dict(archive_url, date_format)
    archive_year, archive_month, archive_day, original_url = m.groups()
    original_dict = {}
    thread = Thread(target=og_url_data, args=(original_url, original_dict))
    thread.start()
    archive_dict = url_data(archive_url)
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
            archive_dict['url-status'] = 'live'
        else:
            # and original title is the same as archive title. Otherwise it
            # means that the content probably has changed and the original data
            # cannot be trusted.
            archive_dict['url-status'] = 'unfit'
    else:
        archive_dict['url-status'] = 'dead'
    if archive_dict['website'] == 'Wayback Machine':
        archive_dict['website'] = urlparse(original_url).hostname.replace(
            'www.', ''
        )
    return archive_dict


def og_url_data(ogurl: str, original_dict) -> None:
    """Fill the dictionary with the information found in ogurl."""
    # noinspection PyBroadException
    try:
        original_dict.update(original_url_dict(ogurl))
    except (
        ContentTypeError,
        ContentLengthError,
        CurlError,
    ):
        pass
    except Exception:
        logger.exception(
            'There was an unexpected error in waybackmechine thread'
        )


def original_url_dict(url: str):
    """Return a dictionary only containing required data for og:url."""
    d = {}
    # Creating a thread to request homepage title in background
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname.removeprefix('.www')
    home_thread, home_list = analyze_home(parsed_url)
    url, html = get_html(url)

    if (m := TITLE_TAG(html)) is not None:
        if html_title := m['result']:
            d['html_title'] = html_title
    else:
        html_title = None

    if authors := find_authors(html):
        d['authors'] = authors

    if journal := find_journal(html):
        d['journal'] = journal
        d['cite_type'] = 'journal'
    else:
        d['cite_type'] = 'web'
        d['website'] = find_site_name(
            html,
            html_title,
            url,
            hostname,
            authors,
            home_list,
            home_thread,
        )
    d['title'] = find_title(
        html, html_title, hostname, authors, home_list, home_thread
    )
    return d
