"""All things specifically related to the Google Books website."""


from urllib.parse import parse_qs, urlparse

from langid import classify

from lib.commons import request
from lib.ris import ris_parse
from lib.commons import dict_to_sfn_cit_ref


def googlebooks_scr(parsed_url, date_format='%Y-%m-%d') -> tuple:
    """Create the response namedtuple."""
    parsed_query = parse_qs(parsed_url.query)

    if (id_ := parsed_query.get('id')) is not None:
        volume_id = id_[0]
    else:  # the new URL format
        volume_id = parsed_url.path.rpartition('/')[2]

    dictionary = ris_parse(request(
        f'https://{parsed_url.netloc}/books/download/?id={volume_id}'
        f'&output=ris', spoof=True).content.decode('utf8'))
    dictionary['date_format'] = date_format
    # manually adding page number to dictionary:
    if (pg := parsed_query.get('pg')) is not None:
        pg0 = pg[0]
        dictionary['page'] = pg0[2:]
        dictionary['url'] += f'&pg={pg0}'
    # although google does not provide a language field:
    if not dictionary['language']:
        dictionary['language'] = classify(dictionary['title'])[0]
    return dict_to_sfn_cit_ref(dictionary)
