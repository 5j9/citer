from threading import Thread
from urllib.parse import urlparse

from lib.commons import request, dict_to_sfn_cit_ref
from lib.bibtex import parse as bibtex_parse


def jstor_scr(url: str, date_format: str = '%Y-%m-%d') -> tuple:
    open_access = []
    thread = Thread(target=is_open_access, args=(url, open_access))
    thread.start()
    id_ = urlparse(url).path.rpartition('/')[2]
    bibtex = request('https://www.jstor.org/citation/text/' + id_).text
    dictionary = bibtex_parse(bibtex)
    dictionary['jstor'] = id_
    dictionary['date_format'] = date_format
    thread.join()
    if open_access:
        dictionary['jstor-access'] = 'free'
    return dict_to_sfn_cit_ref(dictionary)


def is_open_access(url: str, result: list):
    if '"openAccess" : "True"' in request(url, spoof=True).text:
        result.append(True)
