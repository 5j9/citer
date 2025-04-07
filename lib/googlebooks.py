from urllib.parse import ParseResult, parse_qs

from curl_cffi import CurlError
from langid import classify

from lib import request
from lib.citoid import citoid_data
from lib.ris import ris_parse
from lib.urls import url_data


def google_books_data(parsed_url: ParseResult) -> dict:
    parsed_query = parse_qs(parsed_url.query)

    if (id_ := parsed_query.get('id')) is not None:
        volume_id = id_[0]
    else:  # the new URL format
        path = parsed_url.path
        if path[:7] != '/books/':
            return url_data(parsed_url.geturl())
        volume_id = path.rpartition('/')[2]

    try:
        r = request(
            f'https://{parsed_url.netloc}/books/download/?id={volume_id}'
            f'&output=ris',
            spoof=True,
        )
    except CurlError:
        dictionary = None
    else:
        dictionary = ris_parse(r.content.decode('utf8'))
    if dictionary is None:
        dictionary = citoid_data(parsed_url.geturl(), True)
    # manually adding page number to dictionary:
    if (pg := parsed_query.get('pg')) is not None:
        pg0 = pg[0]
        dictionary['page'] = pg0[2:]
        dictionary['url'] += f'&pg={pg0}'
    # although google does not provide a language field:
    if not dictionary['language']:
        dictionary['language'] = classify(dictionary['title'])[0]
    return dictionary
