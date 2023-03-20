from threading import Thread
from urllib.parse import urlparse

from lib.bibtex import parse as bibtex_parse
from lib.commons import request


def url_to_dict(url: str, date_format: str = '%Y-%m-%d') -> dict:
    open_access = []
    thread = Thread(target=is_open_access, args=(url, open_access))
    thread.start()
    id_ = urlparse(url).path.rpartition('/')[2]
    bibtex = request('https://www.jstor.org/citation/text/' + id_).content.decode('utf8')
    dictionary = bibtex_parse(bibtex)
    dictionary['jstor'] = id_
    dictionary['date_format'] = date_format
    thread.join()
    if open_access:
        dictionary['jstor-access'] = 'free'
    return dictionary


def is_open_access(url: str, result: list):
    if '"openAccess" : "True"' in request(url, spoof=True).text:
        result.append(True)
