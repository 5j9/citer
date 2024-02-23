from datetime import date
from threading import Thread
from urllib.parse import urlparse

from curl_cffi import CurlError

from lib import logger
from lib.commons import rc
from lib.urls import (
    ContentLengthError,
    ContentTypeError,
    url_data,
)

URL_FULLMATCH = rc(
    r'https?+://web(?:-beta)?+\.archive\.org/(?:web/)?+'
    r'(\d{4})(\d{2})(\d{2})\d{6}(?>cs_|i(?>d_|m_)|js_)?+/(http.*)'
).fullmatch


def archive_org_data(archive_url: str) -> dict:
    if (m := URL_FULLMATCH(archive_url)) is None:
        # Could not parse the archive_url. Treat as an ordinary URL.
        return url_data(archive_url)
    archive_year, archive_month, archive_day, original_url = m.groups()
    original_dict = {}
    thread = Thread(target=og_url_data_tt, args=(original_url, original_dict))
    thread.start()
    archive_dict = url_data(archive_url)
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
            archive_dict |= original_dict
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


def og_url_data_tt(ogurl: str, original_dict) -> None:
    """Fill the dictionary with the information found in ogurl."""
    # noinspection PyBroadException
    try:
        original_dict |= url_data(ogurl)
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
