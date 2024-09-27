from curl_cffi import CurlError
from langid import classify
from lxml.html import HtmlElement, fromstring

from lib import logger, request
from lib.commons import first_last, rc

AUTHORS_FINDALL = rc(r'(\S+?)\s*+:\s*+(.*)').findall
VOLUME_SEARCH = rc(r'\bجلد (\d+)').search


def ketabir_data(url: str) -> dict:
    dictionary: dict = _url_data(url)  # type: ignore
    if 'language' not in dictionary:
        # Assume that language is either fa or en.
        # Todo: give warning about this assumption?
        dictionary['language'] = classify(dictionary['title'])[0]
    return dictionary


def isbn_to_url(isbn: str) -> str | None:
    """Return the ketab.ir book-url for the given isbn."""
    r = request(f'https://msapi.ketab.ir/search/?query={isbn}&limit=1')
    j = r.json()
    return (
        'https://ketab.ir/book/'
        + j['result']['groups']['printableBook']['items'][0]['url']
    )


def _url_data(ketabir_url: str) -> dict | None:
    try:
        # Try to see if ketabir is available,
        # ottobib should continue its work in isbn.py if it is not.
        r = request(ketabir_url)
    except CurlError:
        logger.exception(ketabir_url)
        return

    soup: HtmlElement = fromstring(r.content)
    d = {
        'cite_type': 'book',
        'title': soup.xpath('.//*[contains(@class, "card-title")][1]')[0]
        .text_content()
        .strip(),
    }

    table: dict[str, HtmlElement] = {
        (tds := tr.xpath('.//td'))[0].text: tds[1]
        for tr in soup.xpath('.//tr')
    }
    # initiating name lists:
    others = []
    authors = []
    editors = []
    translators = []
    # building lists:
    for span in table['پدیدآور'].xpath('.//span'):
        role = span.text.strip(' :\n')
        name = span.xpath('.//a[1]/text()')[0]
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

    d['publisher'] = table['ناشر'].xpath('.//a[1]/text()')[0].strip()

    if len(date := table['تاریخ نشر'].text.strip()) == 8 and date.isdecimal():
        d['month'] = date[4:6]
        d['year'] = date[:4]

    d['isbn'] = table['شابک'].text

    if loc := table['محل نشر'].text.strip():
        d['publisher-location'] = loc

    if m := VOLUME_SEARCH(table['توضیحات'].text):
        d['volume'] = m[1]

    return d
