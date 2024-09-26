from urllib.parse import parse_qs

from langid import classify

from lib import request
from lib.ris import ris_parse
from lib.urls import url_data


def google_books_data(parsed_url) -> dict:
    parsed_query = parse_qs(parsed_url.query)

    if (id_ := parsed_query.get('id')) is not None:
        volume_id = id_[0]
    else:  # the new URL format
        path = parsed_url.path
        if path[:7] != '/books/':
            return url_data(parsed_url.geturl())
        volume_id = path.rpartition('/')[2]

    dictionary = ris_parse(
        request(
            f'https://{parsed_url.netloc}/books/download/?id={volume_id}'
            f'&output=ris',
            spoof=True,
        ).content.decode('utf8')
    )
    # manually adding page number to dictionary:
    if (pg := parsed_query.get('pg')) is not None:
        pg0 = pg[0]
        dictionary['page'] = pg0[2:]
        dictionary['url'] += f'&pg={pg0}'
    # although google does not provide a language field:
    if not dictionary['language']:
        dictionary['language'] = classify(dictionary['title'])[0]
    return dictionary
