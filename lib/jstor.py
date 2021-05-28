from urllib.parse import urlparse

from lib.commons import request, dict_to_sfn_cit_ref
from lib.ris import ris_parse


def jstor_scr(url: str, date_format: str = '%Y-%m-%d') -> tuple:
    _, _, id_ = urlparse(url).path.rpartition('/')
    dictionary = ris_parse(request('https://www.jstor.org/citation/ris/10.2307/' + id_).text)
    dictionary['date_format'] = date_format
    return dict_to_sfn_cit_ref(dictionary)
