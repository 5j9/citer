from unittest.mock import Mock, patch
from urllib.parse import urlparse

from pytest import mark, raises

from lib.commons import data_to_sfn_cit_ref
from lib.googlebooks import google_books_data


def _googlebooks_scr(url):
    return data_to_sfn_cit_ref(google_books_data(url))


def googlebooks_scr(url):
    return _googlebooks_scr(urlparse(url))


def test_gb1():
    assert (
        '* {{cite book '
        '| last=Arms '
        '| first=W.Y. '
        '| title=Digital Libraries '
        '| publisher=MIT Press '
        '| series=Digital Libraries and Electronic Publishing '
        '| year=2001 '
        '| isbn=978-0-262-26134-0 '
        '| url=https://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11 '
        '| access-date='
    ) in googlebooks_scr(
        'http://books.google.com/books?'
        'id=pzmt3pcBuGYC&pg=PR11&lpg=PP1&dq=digital+library'
    )[1]


def test_gb2():
    """a book with more than 4 authors (10 authors)"""
    o = googlebooks_scr(
        'http://books.google.com/books?'
        'id=U46IzqYLZvAC&pg=PT57#v=onepage&q&f=false'
    )
    assert (
        '{{sfn '
        '| Anderson '
        '| DeBolt '
        '| Featherstone '
        '| Gunther '
        '| 2010 '
        '| p=57}}'
    ) in o[0]
    assert (
        '* {{cite book '
        '| last=Anderson '
        '| first=E. '
        '| last2=DeBolt '
        '| first2=V. '
        '| last3=Featherstone '
        '| first3=D. '
        '| last4=Gunther '
        '| first4=L. '
        '| last5=Jacobs '
        '| first5=D.R. '
        '| last6=Mills '
        '| first6=C. '
        '| last7=Schmitt '
        '| first7=C. '
        '| last8=Sims '
        '| first8=G. '
        '| last9=Walter '
        '| first9=A. '
        '| last10=Jensen-Inman '
        '| first10=L. '
        '| title=InterACT with Web Standards: '
        'A holistic approach to web design '
        '| publisher=Pearson Education '
        '| series=Voices That Matter '
        '| year=2010 '
        '| isbn=978-0-13-270490-8 '
        '| url=https://books.google.com/books?id=U46IzqYLZvAC&pg=PT57 '
        '| access-date='
    ) in o[1]


def test_gb3():
    """Non-ascii characters in title (Some of them where removed later)"""
    o = googlebooks_scr(
        'http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588&dq=%22a+'
        'Delimiter+is%22&hl=en&sa=X&ei=oNKSUrKeDovItAbO_4CoBA&ved='
        '0CC4Q6AEwAA#v=onepage&q=%22a%20Delimiter%20is%22&f=false'
    )
    assert '{{sfn | Farrell | 2009 | p=588}}' in o[0]
    assert (
        '* {{cite book '
        '| last=Farrell '
        '| first=J. '
        '| title=Microsoft Visual C# 2008 Comprehensive: '
        'An Introduction to Object-Oriented Programming '
        '| publisher=Cengage Learning '
        '| year=2009 '
        '| isbn=978-1-111-78619-9 '
        '| url=https://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588 '
        '| access-date='
    ) in o[1]


@mark.xfail
def test_gb4():
    """Non-ascii characters in author's name."""
    o = googlebooks_scr(
        'https://books.google.com/books?id='
        'i8nZjjo_9ikC&pg=PA229&dq=%22legal+translation+is%22&hl=en&sa='
        'X&ei=hEuYUr_mOsnKswb49oDQCA&ved=0CC4Q6AEwAA#v=onepage&q='
        '%22legal%20translation%20is%22&f=false'
    )
    assert '{{sfn | Šarčević | 1997 | p=229}}' in o[0]
    assert (
        '* {{cite book '
        '| last=Šarčević '
        '| first=S. '
        '| title=New Approach to Legal Translation '
        '| publisher=Springer Netherlands '
        '| year=1997 '
        '| isbn=978-90-411-0401-4 '
        '| url=https://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229 '
        '| access-date='
    ) in o[1]


def test_gb5():
    """ref checking"""
    o = googlebooks_scr(
        'https://encrypted.google.com/books?id=6upvonUt0O8C&pg=PA378&'
        'dq=density+of+granite&hl=en&sa=X&ei=YBHIU-qCBIyX0QXusoDgAg&ved='
        '0CEIQ6AEwBjgK#v=onepage&q=density%20of%20granite&f=false'
    )
    assert (
        '* {{cite book '
        '| last=Serway '
        '| first=R.A. '
        '| last2=Jewett '
        '| first2=J.W. '
        '| title=Physics for Scientists and Engineers, Volume 1, '
        'Chapters 1-22 | publisher=Cengage Learning '
        '| series=Physics for Scientists and Engineers '
        '| year=2009 '
        '| isbn=978-1-4390-4838-2 '
        '| url=https://books.google.com/books?id=6upvonUt0O8C&pg=PA378'
        ' '
        '| access-date='
    ) in o[1]
    assert (
        '<ref name="w724">'
        '{{cite book '
        '| last=Serway '
        '| first=R.A. '
        '| last2=Jewett '
        '| first2=J.W. '
        '| title=Physics for Scientists and Engineers, Volume 1, '
        'Chapters 1-22 | publisher=Cengage Learning '
        '| series=Physics for Scientists and Engineers '
        '| year=2009 '
        '| isbn=978-1-4390-4838-2 '
        '| url=https://books.google.com/books?id=6upvonUt0O8C&pg=PA378'
        ' '
        '| access-date='
    ) in o[2]
    assert ' | page=378}}</ref>' in o[2]


@patch('lib.googlebooks.url_data', side_effect=NotImplementedError)
def test_ngram_url(url_data: Mock):
    url = 'https://books.google.com/ngrams/graph?content=countermeasure&year_start=1740&year_end=1760&corpus=en-2019&smoothing=3'
    with raises(NotImplementedError):
        google_books_data(urlparse(url))
    url_data.assert_called_once_with(url)
