from datetime import date
from threading import Thread
from urllib.parse import urlparse

from curl_cffi import CurlError
from regex import Match

from lib import logger
from lib.commons import rc
from lib.urls import (
    ContentLengthError,
    ContentTypeError,
    url_data,
    url_text,
)

archive_org_url_match = rc(
    r'https?://web(?:-beta)?\.archive\.org/(?:web/)?'
    r'(\d{4})(\d{2})(\d{2})\d{6}(?:cs_|i(?:d_|m_)|js_)?/(\S*)'
).match

archive_today_url_search = rc(
    r'(?<=<link rel="canonical" href=")https://archive.ph/(\d{4}).(\d{2}).(\d{2})-[^/]*/(http[^"]*)"'
).search


def _archive_data(archive_url: str, m: Match, archive_html: str):
    archive_year, archive_month, archive_day, original_url = m.groups()
    if not original_url.startswith('http'):
        original_url = 'http://' + original_url

    og_d = {}
    og_thread = Thread(target=og_url_data_tt, args=(original_url, og_d))
    og_thread.start()

    d = url_data(archive_url, check_home=False, html=archive_html)
    d['url'] = original_url
    d['archive-url'] = archive_url
    d['archive-date'] = date(
        int(archive_year), int(archive_month), int(archive_day)
    )

    og_thread.join()
    if og_d and og_d['url'] == d['url']:
        # The og_url has been successfully scraped (not a redirect),
        if (
            og_d['title'] == d['title']
            or og_d['html_title'] == d['html_title']
        ):
            # and original title is the same as archive title
            d |= og_d
            d['url-status'] = 'live'
        else:
            # otherwise title does not match, meaning that the content
            # probably has changed and the original data cannot be trusted
            d['url-status'] = 'unfit'
    else:
        d['website'] = urlparse(original_url).hostname.removeprefix('www.')
        d['url-status'] = 'dead'
    return d


def archive_today_data(archive_url: str) -> dict:
    _, archive_html = url_text(archive_url)
    if (m := archive_today_url_search(archive_html)) is None:
        # Could not parse the archive_url. Treat as an ordinary URL.
        return url_data(archive_url, html=archive_html)
    return _archive_data(archive_url, m, archive_html)


def archive_org_data(archive_url: str) -> dict:
    if (m := archive_org_url_match(archive_url)) is None:
        # Could not parse the archive_url. Treat as an ordinary URL.
        return url_data(archive_url)
    _, archive_html = url_text(archive_url)
    return _archive_data(archive_url, m, archive_html)


def og_url_data_tt(og_url: str, og_d: dict, /) -> None:
    """Fill the dictionary with the information found in ogurl."""
    # noinspection PyBroadException
    try:
        og_d |= url_data(og_url, this_domain_only=True)
    except (
        ContentTypeError,
        ContentLengthError,
        CurlError,
    ):
        pass
    except Exception:
        logger.exception(
            'There was an unexpected error in waybackmachine thread'
        )
