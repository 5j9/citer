from datetime import date as datetime_date
from difflib import get_close_matches
from functools import partial
from html import unescape as html_unescape
from logging import getLogger
from threading import Thread
from typing import Any
from urllib.parse import urlparse

from httpx import HTTPError, Response, TimeoutException
from langid import classify

from lib.citoid import get_citoid_dict
from lib.commons import ANYDATE_PATTERN, Search, find_any_date, rc, request
from lib.doi import get_crossref_dict
from lib.urls_authors import CONTENT_ATTR, IV, find_authors

MAX_RESPONSE_LENGTH = 10_000_000  # in bytes


# https://stackoverflow.com/questions/3458217/how-to-use-regular-expression-to-match-the-charset-string-in-html
CHARSET = rc(
    rb"""
    <meta(?!\s*+(?>name|value)\s*+=)[^>]*?charset\s*+=[\s"']*+([^\s"'/>]*)
    """,
    IV,
).search

TITLE_META_NAME_OR_PROP = r"""
    (?>name|property)=(?<q>["\'])
        (?>citation_title|title|Headline|og:title)
    (?P=q)
"""
TITLE_SEARCH = rc(
    r'<meta\s++(?:'
    + TITLE_META_NAME_OR_PROP
    + r'\s++'
    + CONTENT_ATTR
    + '|'
    + CONTENT_ATTR
    + r'\s++'
    + TITLE_META_NAME_OR_PROP
    + ')'
    '|'
    r'class=(?<q>["\'])(?>main-hed|heading1)(?P=q)[^>]++>(?<result>[^<]*+)<',
    IV,
).search

TITLE_TAG = rc(
    r"""
    <title\b[^>]*+>
        (?P<result>[^<]++[\s\S]*?)
    </title\s*+>
    """,
    IV,
).search

DATE_META_NAME_OR_PROP = r"""
    (?>name|property)=(?<q>["\'])(?>
        article:(?>modified_time|published_time)
        |citation_(?>date|publication_date)
        |date
        |DC.date.[^'"\n>]*+
        |last-modified
        |pub_?date
        |sailthru\.date
    )(?P=q)
"""
DATE_CONTENT_ATTR = (
    r'content=(?<q>["\'])(?>' + ANYDATE_PATTERN + r'|(?<year_only>\d{4})'
    r'(?P=q))'
)
DATE_SEARCH = rc(
    r'<meta\s+[^\n<]*?(?:'
    + DATE_META_NAME_OR_PROP
    + r'\s++[^\n<]*?'
    + DATE_CONTENT_ATTR
    + '|'
    + DATE_CONTENT_ATTR
    + r'\s++[^\n<]*?'
    + DATE_META_NAME_OR_PROP
    + ')'
    '|'
    # http://livescience.com/46619-sterile-neutrino-experiment-beginning.html
    # https://www.thetimes.co.uk/article/woman-who-lost-brother-on-mh370-mourns-relatives-on-board-mh17-r07q5rwppl0
    r'date(?>Published|line)[^\w]++' + ANYDATE_PATTERN,
    IV,
).search


def meta_searcher(names: list) -> Search:
    name_or_prop = r'(?>name|property)=(?<q>["\'])\L<names>(?P=q)'
    return rc(
        r'<meta\s++[^\n<]*?(?:'
        + CONTENT_ATTR
        + r'\s++[^\n<]*?'
        + name_or_prop
        + '|'
        + name_or_prop
        + r'\s++[^\n<]*?'
        + CONTENT_ATTR
        + ')',
        IV,
        names=names,
    ).search


JOURNAL_TITLE_SEARCH = meta_searcher(['citation_journal_title'])
PUBLISHER_SEARCH = meta_searcher(['DC.publisher', 'citation_publisher'])
ISSN_SEARCH = meta_searcher(['citation_issn'])
PMID_SEARCH = meta_searcher(['citation_pmid'])
DOI_SEARCH = meta_searcher(['citation_doi'])
VOLUME_SEARCH = meta_searcher(['citation_volume'])
ISSUE_SEARCH = meta_searcher(['citation_issue'])
FIRST_PAGE_SEARCH = meta_searcher(['citation_firstpage'])
LAST_PAGE_SEARCH = meta_searcher(['citation_lastpage'])
SITE_NAME_SEARCH = meta_searcher(['og:site_name'])

TITLE_SEPS = {' - ', ' — ', '|'}  # keep ins sync with <1>
TITLE_SPLIT = rc(r'\L<title_seps>', title_seps=TITLE_SEPS).split
LANG_SEARCH = rc(r'\slang=["\']?([a-z]{2})\b').search


class ContentTypeError(ValueError):

    """Raise when content-type header does not start with 'text/'."""

    pass


class ContentLengthError(ValueError):
    """Raise when content-length header indicates a very long content."""


class StatusCodeError(ValueError):
    """Raise when status_code != 200."""


# inaccurate but should be faster than bs4
# https://stackoverflow.com/questions/14694482/converting-html-to-text-with-python
to_text = partial(rc(r'<[^>]*+>').sub, '')


def url_to_dict(url: str, date_format: str = '%Y-%m-%d', /) -> dict:
    """Create the response namedtuple."""
    dictionary = url2dict(url)
    dictionary['date_format'] = date_format
    return dictionary


def find_journal(html: str) -> str | None:
    """Return journal title as a string."""
    # http://socialhistory.ihcs.ac.ir/article_319_84.html
    if (m := JOURNAL_TITLE_SEARCH(html)) is not None:
        return m['result']


def find_publisher(html: str) -> str | None:
    if (m := PUBLISHER_SEARCH(html)) is None:
        return None
    publisher = m['result']
    if '|' in publisher:
        return None
    return publisher


def find_issn(html: str) -> str | None:
    r"""Return International Standard Serial Number as a string.

    Normally ISSN should be in the  '\d{4}\-\d{3}[\dX]' format, but this
    function does not check that.
    """
    if (m := ISSN_SEARCH(html)) is not None:
        return m['result']


def find_pmid(html: str) -> str | None:
    """Return pmid as a string."""
    if (m := PMID_SEARCH(html)) is not None:
        return m['result']


def find_doi(html: str) -> str | None:
    """Return DOI as a string."""
    if (m := DOI_SEARCH(html)) is not None:
        return m['result']


def find_volume(html: str) -> str | None:
    """Return citatoin volume number as a string."""
    if (m := VOLUME_SEARCH(html)) is not None:
        return m['result']


def find_issue(html: str) -> str | None:
    """Return citation issue number as a string."""
    if (m := ISSUE_SEARCH(html)) is not None:
        return m['result']


def find_pages(html: str) -> str | None:
    """Return citation pages as a string."""
    # http://socialhistory.ihcs.ac.ir/article_319_84.html
    if fp_match := FIRST_PAGE_SEARCH(html):
        if lp_match := LAST_PAGE_SEARCH(html):
            return fp_match['result'] + '–' + lp_match['result']


def find_site_name(
    html: str,
    html_title: str,
    url: str,
    hostname: str,
    authors: list[tuple[str, str]],
    home_list: list[str],
    thread: Thread,
) -> str:
    """Return (site's name as a string, where).

    Parameters:
        html: The html string of the page being processed.
        html_title: Title of the page found in the title tag of the html.
        url: URL of the page.
        hostname: urlparse(url).hostname.removeprefix('www.')
        authors: Authors list returned from find_authors function.
        home_list: A list containing the title of the home page as a str.
        thread: The thread that should be joined before using home_title list.
    Returns site's name as a string.
    """
    if (m := SITE_NAME_SEARCH(html)) is not None:
        return m['result'].partition('|')[0].rstrip()
    # search the title
    if html_title is not None:
        if site_name := parse_title(
            html_title, hostname, authors, home_list, thread
        )[2]:
            return site_name
    # noinspection PyBroadException
    try:
        # using home_title
        thread.join()
        home_site_name, home_title = home_list
        if home_site_name is not None:
            return home_site_name
        if home_title is None:
            return hostname
        if (i := home_title.find(':')) != -1:
            if site_name := home_title[:i].strip():
                return site_name
        if site_name := parse_title(home_title, hostname, None)[2]:
            return site_name
        return home_title.partition('|')[0]
    except Exception:
        logger.exception(url)
    # return hostname
    return hostname


def find_title(
    html: str,
    html_title: str,
    hostname: str,
    authors: list[tuple[str, str]],
    home_list: list[str],
    thread: Thread,
) -> str | None:
    """Return (title_string, where_info)."""
    if (m := TITLE_SEARCH(html)) is not None:
        return parse_title(
            html_unescape(m['result']),
            hostname,
            authors,
            home_list,
            thread,
        )[1]
    elif html_title is not None:
        return parse_title(html_title, hostname, authors, home_list, thread)[1]
    else:
        return None


def parse_title(
    title: str,
    hostname: str,
    authors: list[tuple[str, str]] | None,
    home_list: list[str | None] | None = None,
    thread: Thread = None,
) -> tuple[str | None, str, str | None]:
    """Return (intitle_author, pure_title, intitle_sitename).

    Examples:

    >>> parse_title("Rockhopper raises Falklands oil estimate - FT.com",
            "http://www.ft.com/cms/s/ea29ffb6-c759-11e0-9cac-00144feabdc0",
            None)
    (None, 'Rockhopper raises Falklands oil estimate', 'FT.com')

    >>> parse_title('some title - FT.com - something unknown',
            "http://www.ft.com/cms/s/ea29ffb6-c759-11e0-9cac-00144feabdc0",
            None)
    (None, 'some title - something unknown', 'FT.com')

    >>> parse_title("Alpha decay - Wikipedia, the free encyclopedia",
            "https://en.wikipedia.org/wiki/Alpha_decay",
            None)
    (None, 'Alpha decay', 'Wikipedia, the free encyclopedia')

    >>> parse_title("	BBC NEWS | Health | New teeth 'could soon be grown'",
            'http://news.bbc.co.uk/2/hi/health/3679313.stm',
            None)
    (None, "Health - New teeth 'could soon be grown'", 'BBC NEWS')

    """
    intitle_author = intitle_sitename = None
    parts = TITLE_SPLIT(title.strip())
    if len(parts) == 1:
        return None, title, None
    parts_map: dict[str, str] = {p.lower(): p for p in parts}
    # Searching for intitle_sitename
    # 1. In hostname
    for part in parts_map:
        if (part in hostname) or not (
            set(part.split()) - set(hostname.split('.'))
        ):
            intitle_sitename = parts_map.pop(part).strip()
            break
    else:
        # 2. Using difflib on hostname
        # Cutoff = 0.3: 'BBC - Homepage' will match u'‭BBC ‮فارسی‬'
        if close_matches := get_close_matches(
            hostname, parts_map, n=1, cutoff=0.3
        ):
            part = close_matches[0]
            intitle_sitename = parts_map.pop(part).strip()
        else:
            if thread is not None:
                thread.join()
            if home_list is not None:
                home_site_name, home_title = home_list
                if home_title is not None:
                    # 3. In homepage title
                    for part in parts_map:
                        if part in home_title:
                            intitle_sitename = parts_map.pop(part).strip()
                            break
                    else:
                        # 4. Using difflib on home_title
                        if close_matches := get_close_matches(
                            home_title, parts_map, n=1, cutoff=0.3
                        ):
                            part = close_matches[0]
                            intitle_sitename = parts_map.pop(part).strip()
    # Searching for intitle_author
    if authors and len(parts_map) > 1:
        for first, last in authors:
            for part in parts_map:
                if last.lower() in part:
                    intitle_author = parts_map.pop(part).strip()
                    break
    # keep strip chars in sync with <1>
    # pure_title = ' — '.join(parts.values()).strip('-|— ').partition('|')[0]
    pure_title: str = max(parts_map.values(), key=len)
    return intitle_author, pure_title, intitle_sitename


def find_date(html: str, url: str) -> datetime_date:
    """Return the date of the document."""
    # Example for find_any_date(url):
    # http://ftalphaville.ft.com/2012/05/16/1002861/recap-and-tranche-primer/?Authorised=false
    # Example for find_any_date(html):
    # https://www.bbc.com/news/uk-england-25462900
    if (m := DATE_SEARCH(html)) is not None:
        return m['year_only'] or find_any_date(m)
    return find_any_date(url) or find_any_date(html)


def _analyze_home(parsed_url: tuple, home_list: list) -> None:
    """Append home_title and site_name to home_list.

    home_list is used to return the thread result.
    """
    home_url = '://'.join(parsed_url[:2])
    with request(home_url, spoof=True, stream=True) as r:
        r: Response
        try:
            check_response(r)
        except (
            HTTPError,
            StatusCodeError,
            ContentTypeError,
            ContentLengthError,
        ):
            return
        content = next(r.iter_bytes(MAX_RESPONSE_LENGTH))

    m = CHARSET(content)
    html = content.decode(m[1].decode() if m else r.encoding)

    if m := SITE_NAME_SEARCH(html):
        home_list[0] = m['result']

    m = TITLE_TAG(html)
    title = html_unescape(m['result']) if m else None
    home_list[1] = title


def analyze_home(parsed_url: tuple) -> tuple[Thread, list]:
    home_list = [None, None]
    home_thread = Thread(target=_analyze_home, args=(parsed_url, home_list))
    home_thread.start()
    return home_thread, home_list


def check_response(r: Response) -> None:
    """Check content-type and content-length of the response."""
    if r.status_code != 200:
        raise StatusCodeError(r.status_code)
    get_header = r.headers.get
    if (content_type := get_header('content-type')) is not None:
        if not content_type.startswith('text/'):
            raise ContentTypeError(content_type)
    # assume this is a text response
    if (content_length := get_header('content-length')) is None:
        # assume the length is OK, there is another check later
        return
    bytes_length = int(content_length)
    if bytes_length > MAX_RESPONSE_LENGTH:
        raise ContentLengthError(
            'Content-length was too long. '
            f'({bytes_length / 1000000:.2f} MB)'
        )


def get_html(url: str) -> tuple[str, str]:
    """Return the html string for the given url."""
    r: Response
    with request(url, spoof=True, stream=True) as r:
        check_response(r)
        size = 0
        chunks = []
        a = chunks.append
        for chunk in r.iter_bytes(MAX_RESPONSE_LENGTH):
            size += len(chunk)
            if size >= MAX_RESPONSE_LENGTH:
                raise ValueError(
                    'response was too large: '
                    f'{size=} > {MAX_RESPONSE_LENGTH=}'
                )
            a(chunk)
        content = b''.join(chunks)
    charset_match = CHARSET(content)
    return str(r.url), content.decode(
        charset_match[1].decode() if charset_match else r.encoding
    )


def url2dict(url: str) -> dict[str, Any]:
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname.replace('www.', '', 1)

    home_thread, home_list = analyze_home(parsed_url)

    try:
        url, html = get_html(url)
    except (StatusCodeError, TimeoutException):
        # sometimes get_html fails (is blacklisted), but zotero works
        # issues/47
        if (d := get_citoid_dict(url, True)) is None:
            raise
        d['url'] = url
        return d
    except ContentTypeError:
        return {'url': url, 'cite_type': 'web'}

    d = {'url': url}

    if doi := find_doi(html):
        # noinspection PyBroadException
        try:
            return get_crossref_dict(doi)
        except Exception:
            logger.exception(f'{url=}, {doi=}')
            d['doi'] = doi

    if m := TITLE_TAG(html):
        if html_title := html_unescape(m['result']):
            d['html_title'] = html_title
    else:
        html_title = None
    # d['html_title'] is used in waybackmechine.py.
    if authors := find_authors(html):
        d['authors'] = authors
    d['issn'] = find_issn(html)
    d['pmid'] = find_pmid(html)
    d['volume'] = find_volume(html)
    d['issue'] = find_issue(html)
    d['page'] = find_pages(html)
    d['journal'] = find_journal(html)
    publisher = d['publisher'] = find_publisher(html)
    if d['journal']:
        d['cite_type'] = 'journal'
    else:
        d['cite_type'] = 'web'
        if publisher is None:
            d['website'] = find_site_name(
                html,
                html_title,
                url,
                hostname,
                authors,
                home_list,
                home_thread,
            )
    if (
        title := find_title(
            html, html_title, hostname, authors, home_list, home_thread
        )
    ) is not None:
        d['title'] = title.strip()
    if date := find_date(html, url):
        d['date'] = date

    if (lang_match := LANG_SEARCH(html)) is not None:
        d['language'] = lang_match[1]
    else:
        d['language'] = classify(html)[0]

    return d


logger = getLogger(__name__)
