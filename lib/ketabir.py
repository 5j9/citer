from logging import getLogger
from typing import Optional

from bs4 import BeautifulSoup
from langid import classify
from httpx import HTTPError

from lib.commons import first_last, rc, request

AUTHORS_FINDALL = rc(r'(\S+?)\s*+:\s*+(.*)').findall
VOLUME_SEARCH = rc(r'\bجلد (\d+)').search


def url_to_dict(url: str, date_format='%Y-%m-%d', /) -> dict:
    dictionary = _url_to_dict(url)
    dictionary['date_format'] = date_format
    if 'language' not in dictionary:
        # Assume that language is either fa or en.
        # Todo: give warning about this assumption?
        dictionary['language'] = classify(dictionary['title'])[0]
    return dictionary


def isbn_to_url(isbn: str) -> Optional[str]:
    """Return the ketab.ir book-url for the given isbn."""
    r = request(f'https://msapi.ketab.ir/search/?query={isbn}&limit=1')
    j = r.json()
    return (
        'https://ketab.ir/book/'
        + j['result']['groups']['printableBook']['items'][0]['url']
    )


def _url_to_dict(ketabir_url: str) -> Optional[dict]:
    try:
        # Try to see if ketabir is available,
        # ottobib should continue its work in isbn.py if it is not.
        r = request(ketabir_url)
    except HTTPError:
        logger.exception(ketabir_url)
        return

    soup = BeautifulSoup(r.content, features='lxml')
    d = {'cite_type': 'book'}
    d['title'] = soup.select_one('.card-title').text.strip()

    table = {
        (tds := tr.select('td'))[0].text: tds[1] for tr in soup.select('tr')
    }

    # initiating name lists:
    others = []
    authors = []
    editors = []
    translators = []
    # building lists:
    for span in table['پدیدآور'].select('span'):
        role = span.find(string=True).strip(' :\n')
        name = span.select_one('a').find(string=True)
        name = first_last(name, ' ، ')
        if role == 'نويسنده':
            authors.append(name)
        elif role == 'مترجم':
            translators.append(name)
        elif role == 'ويراستار':
            editors.append(name)
        else:
            others.append(('', f'{name[0]} {name[1]} ({role})'))
    if authors:
        d['authors'] = authors
    if others:
        d['others'] = others
    if editors:
        d['editors'] = editors
    if translators:
        d['translators'] = translators

    d['publisher'] = table['ناشر'].find('a').find(string=True).strip()

    if len(date := table['تاریخ نشر'].text.strip()) == 8 and date.isdecimal():
        d['month'] = date[4:6]
        d['year'] = date[:4]

    d['isbn'] = table['شابک'].text

    if loc := table['محل نشر'].text.strip():
        d['publisher-location'] = loc

    if m := VOLUME_SEARCH(table['توضیحات'].text):
        d['volume'] = m[1]

    return d


logger = getLogger(__name__)
