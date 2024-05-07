import datetime

from lib.generator_en import make_ref_name, sfn_cit_ref


def test_do_not_add_page_url():
    d = {
        'url': 'https://www.theguardian.com/us-news/2023/jun/18/alabama'
        '-supreme-court-allen-milligan',
        'html_title': '‘Historic and significant’: key lawyer’s verdict '
        'on Alabama supreme court ruling | US supreme '
        'court | The Guardian',
        'authors': [('Sam', 'Levine')],
        'issn': None,
        'pmid': None,
        'volume': None,
        'issue': None,
        'page': None,
        'journal': None,
        'publisher': None,
        'cite_type': 'web',
        'website': 'the Guardian',
        'title': '‘Historic and significant’: key lawyer’s verdict on '
        'Alabama supreme court ruling',
        'date': datetime.date(2023, 6, 18),
        'language': 'en',
        'date_format': '%Y-%m-%d',
    }
    assert sfn_cit_ref(d)[2][:-18] == (
        '<ref name="i094">{{cite web | last=Levine | first=Sam | title=‘Historic and significant’: key lawyer’s verdict on Alabama supreme court ruling | website=the Guardian | date=2023-06-18 | url=https://www.theguardian.com/us-news/2023/jun/18/alabama-supreme-court-allen-milligan | access-date='
    )


def test_date_does_not_change_ref_name_hash():
    date = datetime.date(2023, 6, 18)
    d = {
        'cite_type': 'web',
        'url': 'https://1.com/',
        'date': date,
        'archive-url': 'https://1.com/',
        'archive-date': date,
        'url-status': 'dead',
        'title': 'T',
        'date_format': '%Y-%m-%d',
    }
    g = d.get
    h1 = make_ref_name(g)
    scr1 = sfn_cit_ref(d)
    assert h1 in scr1[2]
    assert scr1 != sfn_cit_ref(d, '%d-%m-%Y')  # date_format changes output
    assert h1 == make_ref_name(g)  # but hashes are the same
