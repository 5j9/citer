#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Codes used for parsing contents of an arbitrary URL."""


from collections import defaultdict
from datetime import date as datetime_date
from difflib import get_close_matches
from html import unescape as html_unescape
import logging
import re
from threading import Thread
from urllib.parse import urlparse

import regex
from requests import get as requests_get
from requests import head as requests_head
from requests.exceptions import RequestException
from bs4 import SoupStrainer, BeautifulSoup

from commons import (
    find_any_date, detect_language, Response, USER_AGENT_HEADER,
    dictionary_to_response, ANYDATE_PATTERN,
)
from urls_authors import find_authors


# https://stackoverflow.com/questions/3458217/how-to-use-regular-expression-to-match-the-charset-string-in-html
CHARSET = re.compile(
    rb'''<meta(?!\s*(?:name|value)\s*=)[^>]*?charset\s*=[\s"']*([^\s"'/>]*)''',
    re.IGNORECASE,
).search

TITLE_STRAINER = SoupStrainer('title')

CONTENT_ATTR = r'content=(?<q>["\'])(?<result>.+?)(?P=q)'

TITLE_META_NAME = r'name=(?<q>["\'])(?:citation_title|title|Headline)(?P=q)'
TITLE_META_PROP = r'property=(?<q>["\'])og:title(?P=q)'
TITLE_SEARCH = regex.compile(
    rf'''
    <meta\s+(?:
        {TITLE_META_NAME}\s+{CONTENT_ATTR}
        |
        {CONTENT_ATTR}\s+{TITLE_META_NAME}
    )
    |
    class=(?<q>["\'])(?:main-hed|heading1)(?P=q).+?>(?<result>.*?)<
    |
    <meta\s+(?:
        {TITLE_META_PROP}\s+{CONTENT_ATTR}
        |
        {CONTENT_ATTR}\s+{TITLE_META_PROP}
    )
    ''',
    regex.VERBOSE | regex.IGNORECASE,
).search

TITLE_TAG = re.compile(
    r'''
    <title\b[^>]*>
        (?P<result>\s*[\s\S]*?\s*)
    </title\s*>
    ''',
    re.VERBOSE | re.IGNORECASE,
).search

DATE_META_NAME_OR_PROP = r'''
    (?:name|property)=(?<q>["\'])(?:
        citation_date
        |
        citation_publication_date
        |
        last-modified
        |
        article:published_time
        |
        article:modified_time
        |
        pub_?date
        |
        DC\.date\b.*?
        |
        sailthru\.date
        |
        date
    )(?P=q)
'''
DATE_CONTENT_ATTR = rf'''
    content=(?<q>["\'])[^"'<]*?{ANYDATE_PATTERN}[^"'<]*?(?P=q)
'''
DATE_SEARCH = regex.compile(
    rf'''
    <meta\s+(?:
        {DATE_META_NAME_OR_PROP}\s+[^\n<]*?{DATE_CONTENT_ATTR}
        |
        {DATE_CONTENT_ATTR}\s+[^\n<]*?{DATE_META_NAME_OR_PROP}
    )
    |
    # http://livescience.com/46619-sterile-neutrino-experiment-beginning.html
    # https://www.thetimes.co.uk/article/woman-who-lost-brother-on-mh370-mourns-relatives-on-board-mh17-r07q5rwppl0
    (?:datePublished|Dateline)[^\w]+{ANYDATE_PATTERN}
    ''',
    regex.VERBOSE | regex.IGNORECASE,
).search

JOURNAL_META_NAME = r'''
    name=(?<q>["\'])(?:
        citation_journal_title
    )(?P=q)
'''
JOURNAL_TITLE_SEARCH = regex.compile(
    rf'''
    <meta\s+(?:
        {CONTENT_ATTR}\s+[^\n<]*?{JOURNAL_META_NAME}
        |
        {JOURNAL_META_NAME}\s+[^\n<]*?{CONTENT_ATTR}
    )
    ''',
    re.VERBOSE | re.IGNORECASE,
).search


class ContentTypeError(ValueError):

    """Raise when content-type header does not start with 'text/'."""

    pass


class ContentLengthError(ValueError):

    """Raise when content-length header indicates a very long content."""

    pass


class StatusCodeError(ValueError):

    """Raise when requests_get.status_code != 200."""

    pass


def urls_response(url: str, date_format: str= '%Y-%m-%d') -> Response:
    """Create the response namedtuple."""
    try:
        dictionary = url2dict(url)
    except (ContentTypeError, ContentLengthError) as e:
        logger.exception(url)
        return Response(
            sfn='Could not process the request.', cite=e, error=100, ref=''
        )
    dictionary['date_format'] = date_format
    return dictionary_to_response(dictionary)


def find_journal(html: str) -> str:
    """Return journal title as a string."""
    # http://socialhistory.ihcs.ac.ir/article_319_84.html
    m = JOURNAL_TITLE_SEARCH(html)
    if m:
        return m['result'].strip()


def find_url(soup: BeautifulSoup, url: str) -> str:
    """Return og:url or url as a string."""
    # http://www.ft.com/cms/s/836f1b0e-f07c-11e3-b112-00144feabdc0,Authorised=false.html?_i_location=http%3A%2F%2Fwww.ft.com%2Fcms%2Fs%2F0%2F836f1b0e-f07c-11e3-b112-00144feabdc0.html%3Fsiteedition%3Duk&siteedition=uk&_i_referer=http%3A%2F%2Fwww.ft.com%2Fhome%2Fuk
    f = soup.find(attrs={'property': 'og:url'})
    if f:
        ogurl = f['content']
        if urlparse(ogurl).path:
            return ogurl
    return url


def find_issn(soup: BeautifulSoup) -> str:
    """Return International Standard Serial Number as a string.

    Normally ISSN should be in the  '\d{4}\-\d{3}[\dX]' format, but this
    function does not check that.
    """
    # http://socialhistory.ihcs.ac.ir/article_319_84.html
    # http://psycnet.apa.org/journals/edu/30/9/641/
    f = soup.find(attrs={'name': 'citation_issn'})
    if f:
        return f['content'].strip()


def find_pmid(soup: BeautifulSoup) -> str:
    """Return pmid as a string."""
    # http://jn.physiology.org/content/81/1/319
    m = soup.find(attrs={'name': 'citation_pmid'})
    if m:
        return m['content']


def find_doi(soup: BeautifulSoup) -> str:
    """Get the BeautifulSoup object of a page. Return DOI as a string."""
    # http://jn.physiology.org/content/81/1/319
    m = soup.find(attrs={'name': 'citation_doi'})
    if m:
        return m['content']


def find_volume(soup: BeautifulSoup) -> str:
    """Return citatoin volume number as a string."""
    # http://socialhistory.ihcs.ac.ir/article_319_84.html
    m = soup.find(attrs={'name': 'citation_volume'})
    if m:
        return m['content'].strip()


def find_issue(soup: BeautifulSoup) -> str:
    """Return citatoin issue number as a string."""
    # http://socialhistory.ihcs.ac.ir/article_319_84.html
    m = soup.find(attrs={'name': 'citation_issue'})
    if m:
        return m['content'].strip()


def find_pages(soup: BeautifulSoup) -> str:
    """Return citation pages as a string."""
    # http://socialhistory.ihcs.ac.ir/article_319_84.html
    fp = soup.find(attrs={'name': 'citation_firstpage'})
    lp = soup.find(attrs={'name': 'citation_lastpage'})
    if fp and lp:
        return fp['content'].strip() + '–' + lp['content'].strip()


def find_site_name(
    soup: BeautifulSoup,
    url: str,
    authors: list,
    hometitle: list,
    thread: Thread,
) -> str:
    """Return (site's name as a string, where).

    Parameters:
        soup: BeautifulSoup object of the page being processed.
        url: URL of the page.
        authors: Authors list returned from find_authors function.
        hometitle: A list containing hometitle string.
        thread: The thread that should be joined before using hometitle_list.
    Returns site's name as a string.
    """
    find = soup.find
    f = find(attrs={'name': 'og:site_name'})
    if f:
        content = f.get('content')
        if content:
            return content.strip()
    # https://www.bbc.com/news/science-environment-26878529
    f = find(attrs={'property': 'og:site_name'})
    if f:
        content = f.get('content')
        if content:
            return content.strip()
    # http://www.nytimes.com/2007/06/13/world/americas/13iht-whale.1.6123654.html?_r=0
    f = find(attrs={'name': 'PublisherName'})
    if f:
        value = f.get('value')
        if value:
            return value.strip()
    # http://www.bbc.com/news/science-environment-26878529 (Optional)
    f = find(attrs={'name': 'CPS_SITE_NAME'})
    if f:
        content = f.get('content')
        if content:
            return content.strip()
    # http://www.nytimes.com/2013/10/01/science/a-wealth-of-data-in-whale-breath.html
    f = find(attrs={'name': 'cre'})
    if f:
        content = f.get('content')
        if content:
            return content.strip()
    # search the title
    sitename = parse_title(
        soup.title.text, url, authors, hometitle, thread
    )[2]
    if sitename:
        return sitename
    try:
        # using hometitle
        thread.join()
        if ':' in hometitle[0]:
            # http://www.washingtonpost.com/wp-dyn/content/article/2005/09/02/AR2005090200822.html
            sitename = hometitle[0].split(':')[0].strip()
            if sitename:
                return sitename
        sitename = parse_title(hometitle[0], url, None)[2]
        if sitename:
            return sitename
        return hometitle[0]
    except Exception:
        pass
    # return hostname
    hostname = urlparse(url).hostname
    if hostname.startswith('www.'):
        return hostname[4:]
    return hostname


def find_title(
    html: str,
    html_title: str,
    url: str,
    authors: list,
    home_title: list,
    thread: Thread,
) -> str or None:
    """Return (title_string, where_info)."""
    m = TITLE_SEARCH(html)
    if m:
        return parse_title(
            html_unescape(m['result']), url, authors, home_title, thread,
        )[1]
    elif html_title:
        return parse_title(html_title, url, authors, home_title, thread)[1]
    else:
        return None


def parse_title(
    title: str,
    url: str,
    authors: list or None,
    hometitle_list=None,
    thread=None,
) -> tuple:
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
    sep_regex = ' - | — |\|'
    title_parts = re.split(sep_regex, title.strip())
    if len(title_parts) == 1:
        return None, title, None
    hostname = urlparse(url).hostname.replace('www.', '')
    # Searching for intitle_sitename
    # 1. In hostname
    hnset = set(hostname.split('.'))
    for part in title_parts:
        if (part in hostname) or not set(part.lower().split()) - hnset:
            intitle_sitename = part
            break
    if not intitle_sitename:
        # 2. Using difflib on hostname
        # Cutoff = 0.3: 'BBC - Homepage' will match u'‭BBC ‮فارسی‬'
        close_matches = get_close_matches(
            hostname, title_parts, n=1, cutoff=.3
        )
        if close_matches:
            intitle_sitename = close_matches[0]
    if not intitle_sitename:
        if thread:
            thread.join()
        if hometitle_list:
            hometitle = hometitle_list[0]
        else:
            hometitle = ''
        # 3. In homepage title
        for part in title_parts:
            if part in hometitle:
                intitle_sitename = part
                break
    if not intitle_sitename:
        # 4. Using difflib on hometitle
        close_matches = get_close_matches(
            hometitle, title_parts, n=1, cutoff=.3
        )
        if close_matches:
            intitle_sitename = close_matches[0]
    # Remove sitename from title_parts
    if intitle_sitename:
        title_parts.remove(intitle_sitename)
        intitle_sitename = intitle_sitename.strip()
    # Searching for intitle_author
    if authors:
        for author in authors:
            for part in title_parts:
                if author.lastname.lower() in part.lower():
                    intitle_author = part
                    break
    # Remove intitle_author from title_parts
    if intitle_author:
        title_parts.remove(intitle_author)
        intitle_author = intitle_author.strip()
    pure_title = ' - '.join(title_parts)
    return intitle_author, pure_title, intitle_sitename


def find_date(html: str, url: str) -> datetime_date:
    """Get the BeautifulSoup object and url. Return (date_obj, where)."""
    # Example for find_any_date(url):
    # http://ftalphaville.ft.com/2012/05/16/1002861/recap-and-tranche-primer/?Authorised=false
    # Example for find_any_date(soup.text):
    # https://www.bbc.com/news/uk-england-25462900
    m = DATE_SEARCH(html)
    return find_any_date(m) if m else find_any_date(url) or find_any_date(html)


def get_hometitle(url: str, hometitle_list: list) -> None:
    """Get homepage of the url and return it's title.

    hometitle_list will be used to return the thread result.
    This function is invoked through a thread.
    """
    homeurl = '://'.join(urlparse(url)[:2])
    try:
        check_content_headers(homeurl)
        content = requests_get(
            homeurl, headers=USER_AGENT_HEADER, timeout=15
        ).content
        soup = BeautifulSoup(content, 'lxml', parse_only=TITLE_STRAINER)
        hometitle_list.append(soup.title.text.strip())
    except RequestException:
        pass


def check_content_headers(url: str) -> bool:
    """Check content-type and content-length of the response.

    Return True if content-type is text/* and content-length is less than 1MB.
    Also return True if no information is available. Else return False.
    """
    response_headers = requests_head(url, headers=USER_AGENT_HEADER).headers
    if 'content-length' in response_headers:
        megabytes = int(response_headers['content-length']) / 1000000
        if megabytes > 1:
            raise ContentLengthError(
                'Content-length was too long. (' +
                format(megabytes, '.2f') + ' MB)'
            )
    content_type = response_headers.get('content-type')
    if content_type:
        if content_type.startswith('text/'):
            return True
        raise ContentTypeError(
            'Invalid content-type: ' +
            content_type + ' (URL-content is supposed to be text/html)'
        )
    return True


def get_html(url: str) -> tuple:
    """Return the (soup, html) for the given url."""
    check_content_headers(url)
    r = requests_get(url, headers=USER_AGENT_HEADER, timeout=15)
    if r.status_code != 200:
        raise StatusCodeError(r.status_code)
    content = r.content
    charset_match = CHARSET(content)
    return BeautifulSoup(r.content, 'lxml'), content.decode(
        charset_match[1].decode() if charset_match else r.encoding
    )


def url2dict(url: str) -> dict:
    """Get url and return the result as a dictionary."""
    d = defaultdict(lambda: None)
    # Creating a thread to fetch homepage title in background
    home_title_list = []  # A mutable variable used to get the thread result
    home_title_thread = Thread(
        target=get_hometitle, args=(url, home_title_list)
    )
    home_title_thread.start()

    soup, html = get_html(url)
    d['url'] = find_url(soup, url)
    m = TITLE_TAG(html)
    html_title = m['result'] if m else None
    if html_title:
        d['html_title'] = html_title
    # d['html_title'] is used in waybackmechine.py.
    authors = find_authors(soup)
    if authors:
        d['authors'] = authors
    d['doi'] = find_doi(soup)
    d['issn'] = find_issn(soup)
    d['pmid'] = find_pmid(soup)
    d['volume'] = find_volume(soup)
    d['issue'] = find_issue(soup)
    d['page'] = find_pages(soup)
    d['journal'] = find_journal(html)
    if d['journal']:
        d['cite_type'] = 'journal'
    else:
        d['cite_type'] = 'web'
        d['website'] = find_site_name(
            soup, url, authors, home_title_list, home_title_thread
        )
    d['title'] = find_title(
        html, html_title, url, authors, home_title_list, home_title_thread
    )
    date = find_date(html, url)
    if date:
        d['date'] = date
        d['year'] = str(date.year)
    d['language'], d['error'] = detect_language(soup.text)
    return d


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("langid").setLevel(logging.WARNING)
    logger = logging.getLogger()
else:
    logger = logging.getLogger(__name__)
