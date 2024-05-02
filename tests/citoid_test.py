from lib.citoid import citoid_data


def test_url():
    assert citoid_data(
        'https://books.google.com/ngrams/graph?content=countermeasure&year_start=1740&year_end=1760&corpus=en-2019&smoothing=3',
        True,
    ) == {
        'cite_type': 'web',
        'language': 'en',
        'title': 'Google Books Ngram Viewer',
        'website': 'books.google.com',
    }


def test_bad_date():
    assert citoid_data(
        '10.1109/5992.805138',
        True,
    ) == {
        'doi': '10.1109/5992.805138',
        'issue': '6',
        'cite_type': 'journal',
        'page': '79–81',
        'title': 'How to distribute your software over the web',
        'volume': '1',
        'authors': [['N.S.', 'Rebello']],
        'journal': 'Computing in Science & Engineering',
        'date': '1999',
    }
