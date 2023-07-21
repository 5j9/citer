from collections import defaultdict
from datetime import date

from lib.generator_en import sfn_cit_ref


def test_do_not_add_page_url():
    d = defaultdict(
        lambda: None,
        {
            'url': 'https://www.theguardian.com/us-news/2023/jun/18/alabama'
                   '-supreme-court-allen-milligan',
            'html_title': '‘Historic and significant’: key lawyer’s verdict '
                          'on Alabama supreme court ruling | US supreme '
                          'court | The Guardian',
            'authors': [('Sam', 'Levine')], 'issn': None, 'pmid': None,
            'volume': None, 'issue': None, 'page': None, 'journal': None,
            'publisher': None, 'cite_type': 'web', 'website': 'the Guardian',
            'title': '‘Historic and significant’: key lawyer’s verdict on '
                     'Alabama supreme court ruling',
            'date': date(2023, 6, 18), 'language': 'en',
            'date_format': '%Y-%m-%d'
        }
    )
    assert sfn_cit_ref(d)[2][:-18] == (
        '<ref name="Levine 2023 x505">{{cite web | last=Levine | first=Sam | title=‘Historic and significant’: key lawyer’s verdict on Alabama supreme court ruling | website=the Guardian | date=2023-06-18 | url=https://www.theguardian.com/us-news/2023/jun/18/alabama-supreme-court-allen-milligan | access-date='
    )
