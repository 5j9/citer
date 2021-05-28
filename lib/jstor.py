from urllib.parse import urlparse

from lib.commons import request, dict_to_sfn_cit_ref
from lib.ris import ris_parse


def jstor_scr(url: str, date_format: str = '%Y-%m-%d') -> tuple:
    # https://www.jstor.org/stable/resrep26363.7?Search=yes&resultItemClick=true&searchText=google&searchUri=%2Faction%2FdoBasicSearch%3FQuery%3Dgoogle%26acc%3Doff%26wc%3Don%26fc%3Doff%26group%3Dnone%26refreqid%3Dsearch%253A2e627536469ca8786b576957a9797d56&ab_segments=0%2Fbasic_search_gsv2%2Fcontrol&refreqid=fastly-default%3Af90c911269c590baf37330b9d16ae1cd&seq=1#metadata_info_tab_contents
    _, _, id_ = urlparse(url).path.rpartition('/')
    dictionary = ris_parse(request('https://www.jstor.org/citation/ris/10.2307/' + id_).text)
    dictionary['date_format'] = date_format
    return dict_to_sfn_cit_ref(dictionary)
