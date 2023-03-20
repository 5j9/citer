"""Codes specifically related to Noormags website."""

from regex import compile as regex_compile

from lib.bibtex import parse as bibtex_parse
from lib.commons import request

BIBTEX_ARTICLE_ID_SEARCH = regex_compile(
    r'(?<=CitationHandler\.ashx\?id=)\d+').search
RIS_ARTICLE_ID_SEARCH = regex_compile(r'(?<=RIS&id=)\d+').search


def url_to_dict(url: str, date_format: str = '%Y-%m-%d') -> dict:
    dictionary = bibtex_parse(dict_from_bibtex(url))
    dictionary['date_format'] = date_format
    # risr = get_ris(url)[1]
    # dictionary = risr.parse(ris)[1]
    return dictionary


def dict_from_bibtex(noorlib_url):
    """Get bibtex file content from a noormags url. Return as string."""
    pagetext = request(noorlib_url).text
    article_id = BIBTEX_ARTICLE_ID_SEARCH(pagetext)[0]
    url = 'http://www.noorlib.ir/View/HttpHandler/CitationHandler.ashx?id=' +\
          article_id + '&format=BibTex'
    return request(url).text


def dict_from_ris(noorlib_url):
    # This is copied from noormags module (currently not supported but may
    # be)[1]
    """Get ris file content from a noormags url. Return as string."""
    pagetext = request(noorlib_url).text
    article_id = RIS_ARTICLE_ID_SEARCH(pagetext)[0]
    url = 'http://www.noormags.ir/view/CitationHandler.ashx?format=RIS&id=' +\
          article_id
    return request(url).text
