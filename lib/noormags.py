"""Codes specifically related to Noormags website."""

from threading import Thread

from regex import compile as regex_compile

from lib.commons import dict_to_sfn_cit_ref, request
from lib.bibtex import parse as bibtex_parse
from lib.ris import parse as ris_parse


BIBTEX_ARTICLE_ID_SEARCH = regex_compile(r'(?<=/citation/bibtex/)\d+').search
RIS_ARTICLE_ID_SEARCH = regex_compile(r'(?<=/citation/ris/)\d+').search


def noormags_scr(url: str, date_format: str = '%Y-%m-%d') -> tuple:
    """Create the response namedtuple."""
    ris_collection = {}
    ris_thread = Thread(target=ris_fetcher_thread, args=(url, ris_collection))
    ris_thread.start()
    dictionary = bibtex_parse(get_bibtex(url))
    dictionary['date_format'] = date_format
    # language parameter needs to be taken from RIS
    # other information are more accurate in bibtex
    # for example: http://www.noormags.ir/view/fa/articlepage/104040
    # "IS  - 1" is wrong in RIS but "number = { 45 }," is correct in bibtex
    ris_thread.join()
    dictionary.update(ris_collection)
    return dict_to_sfn_cit_ref(dictionary)


def get_bibtex(noormags_url):
    """Get BibTex file content from a noormags_url. Return as string."""
    page_text = request(noormags_url).text
    article_id = BIBTEX_ARTICLE_ID_SEARCH(page_text)[0]
    url = 'http://www.noormags.ir/view/fa/citation/bibtex/' + article_id
    return request(url).text


def get_ris(noormags_url):
    """Get ris file content from a noormags url. Return as string."""
    page_text = request(noormags_url).text
    article_id = RIS_ARTICLE_ID_SEARCH(page_text)[0]
    return request(
        'http://www.noormags.ir/view/fa/citation/ris/' + article_id).text


def ris_fetcher_thread(url, ris_collection):
    """Fill the ris_dict. This function is called in a thread."""
    ris_dict = ris_parse(get_ris(url))
    language = ris_dict.get('language')
    if language:
        ris_collection['language'] = language
    authors = ris_dict.get('authors')
    if authors:
        ris_collection['authors'] = authors
