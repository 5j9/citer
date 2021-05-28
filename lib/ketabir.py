"""All things that are specifically related to adinebook website"""

from collections import defaultdict
from logging import getLogger
from typing import Optional

from langid import classify
from regex import compile as regex_compile
from requests import RequestException
from mechanicalsoup import StatefulBrowser

from lib.commons import first_last, dict_to_sfn_cit_ref, request, USER_AGENT,\
    LANG


ISBN_SEARCH = regex_compile(r'ISBN: </b> ([-\d]++)').search
DATE_SEARCH = regex_compile(
    r'تاریخ نشر:</b>(?<year>\d\d)/(?<month>\d\d)/(?<day>\d\d)').search
PUBLISHER_SEARCH = regex_compile(
    r'Publisher_ctl00_NameLabel" class="linkk">(.*?)</span>').search
VOLUME_SEARCH = regex_compile(r'\bجلد (\d+)').search
TITLE_SEARCH = regex_compile(r'BookTitle" class="h4">([^<]++)').search
AUTHORS_FINDALL = regex_compile(
    r'rptAuthor_ctl\d\d_NameLabel" class="linkk">([^>:]++):([^<]++)<').findall
LOCATION_SEARCH = regex_compile(r'محل نشر:</b>([^<]++)<').search


def ketabir_scr(url: str, date_format='%Y-%m-%d') -> tuple:
    """Return the response namedtuple."""
    dictionary = url2dictionary(url)
    dictionary['date_format'] = date_format
    if 'language' not in dictionary:
        # Assume that language is either fa or en.
        # Todo: give warning about this assumption?
        dictionary['language'] = \
            classify(dictionary['title'])[0]
    return dict_to_sfn_cit_ref(dictionary)


def isbn2url(isbn: str) -> Optional[str]:
    """Return the ketab.ir book-url for the given isbn."""
    browser = StatefulBrowser(user_agent=USER_AGENT)
    browser.open('http://www.ketab.ir/Search.aspx')
    browser.select_form()
    browser['ctl00$ContentPlaceHolder1$TxtIsbn'] = isbn
    browser.submit_selected()
    first_link = browser.get_current_page().select_one('.HyperLink2')
    if first_link is None:
        return
    return browser.absolute_url(first_link['href'])


def url2dictionary(ketabir_url: str) -> Optional[dict]:
    try:
        # Try to see if ketabir is available,
        # ottobib should continoue its work in isbn.py if it is not.
        r = request(ketabir_url)
    except RequestException:
        logger.exception(ketabir_url)
        return
    html = r.content.decode('utf-8')
    d = defaultdict(lambda: None, cite_type='book')
    d['title'] = TITLE_SEARCH(html)[1]
    # initiating name lists:
    others = []
    authors = []
    editors = []
    translators = []
    # building lists:
    for role, name in AUTHORS_FINDALL(html):
        if role == 'نويسنده':
            authors.append(first_last(name))
        elif role == 'مترجم':
            translators.append(first_last(name))
        elif role == 'ويراستار':
            editors.append(first_last(name))
        else:
            others.append(('', f'{name} ({role})'))
    if authors:
        d['authors'] = authors
    if others:
        d['others'] = others
    if editors:
        d['editors'] = editors
    if translators:
        d['translators'] = translators
    m = PUBLISHER_SEARCH(html)
    if m is not None:
        d['publisher'] = m[1]
    m = DATE_SEARCH(html)
    if m is not None:
        if LANG != 'fa':
            d['month'] = m['month']
            d['year'] = '۱۳' + m['year']
        else:
            d['month'] = m['month']
            d['year'] = '۱۳' + m['year']
    m = ISBN_SEARCH(html)
    if m is not None:
        d['isbn'] = m[1]
    m = VOLUME_SEARCH(html)
    if m is not None:
        d['volume'] = m[1]
    m = LOCATION_SEARCH(html)
    if m is not None:
        d['publisher-location'] = m[1]
    return d


logger = getLogger(__name__)
