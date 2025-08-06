from unittest.mock import patch

from pytest import raises

from lib.commons import ReturnError, data_to_sfn_cit_ref, isbn_10or13_search
from lib.isbn_oclc import (
    citoid_data,
    isbn_data,
    oclc_data,
    worldcat_data,
)


def isbn_scr(*args):
    return data_to_sfn_cit_ref(isbn_data(*args))


def oclc_scr(*args):
    return data_to_sfn_cit_ref(oclc_data(*args))


def worldcat_scr(*args):
    return data_to_sfn_cit_ref(worldcat_data(*args))


def test_is1():
    # not in ketabir
    assert isbn_scr('9780349119168', True)[1][:-12] == (
        '* {{cite book | last1=Adkins | first1=Roy A. | last2=Adkins | first2=Lesley | '
        'title=The War for All the Oceans | publisher=Abacus (UK) | '
        'publication-place=London | date=2007 | isbn=978-0-349-11916-8 | '
        'oclc=137313052 | url=https://www.worldcat.org/oclc/137313052 | access-date='
    )


def test_is3():
    # on both ketabid and citoid
    assert isbn_scr('964-6736-34-3 ')[1][:-12] == (
        '* {{cite book | last=Sepehri | first=S. | title=Raz-egole sorkh | '
        'publisher=Muʼassasah-ʼi Intishārāt-i Nigāh | publication-place=Tihrān | '
        'date=2005 | isbn=964-6736-34-3 | oclc=53446327 | url=https://www.worldcat.org/oclc/53446327 | language=fa | access-date='
    )


def test_is4():
    """unpure isbn10 not found in ottobib"""
    assert (
        '* {{cite book | last=حافظ | first=شمس‌الدین‌محمد '
        '| others=رضا نظرزاده (به‌اهتمام) '
        '| title=دیوان کامل حافظ همراه با فالنامه | publisher=دیوان '
        '| publication-place=قم - قم | year=1385 | isbn=964-92962-6-3 '
        '| language=fa}}'
    ) == isbn_scr('choghondar 964-92962-6-3 شلغم')[1]


def test_oclc1():
    assert oclc_scr('875039842')[1] == (
        '* {{cite book | last1=Lewis | first1=James Bryant | last2=Sesay | first2=Amadu | title=Korea and globalization : politics, economics and culture | publisher=RoutledgeCurzon | publication-place=Richmond | year=2002 | isbn=978-0-7007-1512-1 | oclc=875039842}}'
    )


def test_elec_type_with_url():
    assert oclc_scr('809771201')[1] == (
        "* {{cite book | last=Rahman | first=Mizanur | title=MediaWiki Administrators' Tutorial Guide | publisher=Packt Pub. | publication-place=Birmingham | year=2007 | isbn=978-1-84719-045-1 | oclc=809771201}}"
    )


def test_fullname_in_ris():
    assert oclc_scr('24680975')[1] == (
        '* {{cite book '
        '| author=Universidade Federal do Rio de Janeiro '
        '| title=Universidade do Brasil, 1948-1966 '
        '| year=1966 '
        '| oclc=24680975 '
        '| language=pt}}'
    )


def test_hyphened_isbn_match():  # 30
    assert isbn_10or13_search('2-253-00422-7')


def test_citoid_only():  # 31
    assert isbn_scr('3-85673-522-4')[1][:-12] == (
        '* {{cite book | last=Ramseier | first=Walter | title=Münchenstein - Heimatkunde | publication-place=[Liestal] | date=1995 | isbn=3-85673-522-4 | oclc=613273377 | url=https://www.worldcat.org/oclc/613273377 | language=de | access-date='
    )


def test_invalid_oclc():
    with raises(Exception) as e:
        oclc_data('99999999999999')
    assert e.value.args == ('status code was not 2xx',)


def test_oclc_with_issn():
    assert oclc_scr('22239204')[1] == (
        '* {{cite journal | title=73 amateur radio today | publisher=WGE Pub. | publication-place=Hancock, N.H. | year=1990 | issn=1052-2522 | oclc=22239204 | ref={{sfnref|WGE Pub.|1990}}}}'
    )


def test_worldcat_url():
    assert worldcat_scr('https://www.worldcat.org/title/46908525')[1] == (
        '* {{cite book | last1=Lewis | first1=James Bryant | last2=Sesay | first2=Amadu | title=Korea and globalization : politics, economics and culture | publisher=RoutledgeCurzon | publication-place=Richmond | year=2002 | isbn=978-0-7007-1512-1 | oclc=46908525}}'
    )


def test_not_identified_pulisher():
    assert worldcat_scr('https://www.worldcat.org/title/960872319')[1] == (
        '* {{cite book | last=Loftis | first=Cory | title=Before I forget : art of Cory Loftis | year=2105 | isbn=978-0-692-57330-3 | oclc=960872319}}'
    )
    assert worldcat_scr('https://www.worldcat.org/title/650188009')[1] == (
        '* {{cite book | last1=Wilde | first1=Geoff | last2=Braham | first2=Michael | title=Sandgrounders : the complete league history of Southport Football Club | publisher=Carnegie | year=1995 | isbn=978-1-874181-14-9 | oclc=650188009}}'
    )
    assert worldcat_scr('https://www.worldcat.org/title/1051746391')[1] == (
        '* {{cite book | last=Love | first=James Lee | title=Recollections : written in the Library of Congress, Washington, D.C. | year=1921 | oclc=1051746391}}'
    )


def test_citoid():
    assert citoid_data('9781137330963') == {
        'cite_type': 'book',
        'date': '2013',
        'isbn': '978-1-137-33096-3',
        'publisher': 'Palgrave Macmillan',
        'publisher-location': 'New York, NY',
        'title': 'Ethnographies of social support',
    }


@patch('lib.isbn_oclc.google_books')
@patch('lib.isbn_oclc.citoid_thread_target')
def test_not_found_isbn(_m1, _m2):
    with raises(ReturnError) as e:
        isbn_scr('9798863646336')
    assert e.value.args == ('Error: ISBN not found', '', '')


def test_oclc_no_leading_letters():
    assert isbn_scr('978-80-210-8779-8')[1][:-12] == (
        '* {{cite book | title=The European fortune of the Roman Veronica in the Middle Ages | publisher=Brepols | publication-place=Turnhout | date=2017 | isbn=978-80-210-8779-8 | oclc=1021182894 | url=https://www.worldcat.org/title/on1021182894 | ref={{sfnref|Brepols|2017}} | access-date='
    )
