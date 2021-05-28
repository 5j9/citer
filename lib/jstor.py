from urllib.parse import urlparse

from lib.commons import request, dict_to_sfn_cit_ref
from lib.bibtex import parse as bibtex_parse


def jstor_scr(url: str, date_format: str = '%Y-%m-%d') -> tuple:
    id_ = urlparse(url).path.rpartition('/')[2]
    bibtex = request('https://www.jstor.org/citation/text/' + id_).text
    dictionary = bibtex_parse(bibtex)
    dictionary['date_format'] = date_format
    return dict_to_sfn_cit_ref(dictionary)
