from pytest import raises

from lib.commons import ISBN_10OR13_SEARCH, ReturnError, dict_to_sfn_cit_ref
from lib.isbn_oclc import isbn_to_dict, oclc_dict, worldcat_url_to_dict


def isbn_scr(*args):
    return dict_to_sfn_cit_ref(isbn_to_dict(*args))


def oclc_scr(*args):
    return dict_to_sfn_cit_ref(oclc_dict(*args))


def worldcat_scr(*args):
    return dict_to_sfn_cit_ref(worldcat_url_to_dict(*args))


def test_is1():
    # not in ketabir
    assert (
        '* {{cite book '
        '| last=Adkins '
        '| first=Roy '
        '| last2=Adkins '
        '| first2=Lesley '
        '| title=The war for all the oceans : '
        'from Nelson at the Nile to Napoleon at Waterloo '
        '| publisher=Abacus '
        '| publication-place=London '
        '| date=2007 '
        '| isbn=978-0-349-11916-8 '
        '| oclc=137313052}}'
    ) == isbn_scr('9780349119168', True)[1]


def test_is3():
    # on both ketabid and citoid
    assert (
        '* {{cite book | last=Sipihrī | first=Suhrāb. '
        '| title=Rāz-i gul-i surkh '
        '| publisher=Muʼassasah-ʼi Intishārāt-i Nigāh '
        '| publication-place=Tihrān | date=1379 [2000 or 2001] '
        '| isbn=964-6736-34-3 '
        '| oclc=53446327}}'
    ) == isbn_scr('964-6736-34-3 ')[1]


def test_is4():
    """unpure isbn10 not found in ottobib"""
    assert (
        '* {{cite book | last=حافظ | first=شمس‌الدین‌محمد '
        '| others=رضا نظرزاده (به‌اهتمام) '
        '| title=دیوان کامل حافظ همراه با فالنامه | publisher=دیوان '
        '| publication-place=قم - قم | year=1385 | isbn=978-964-92962-6-5 '
        '| language=fa}}'
    ) == isbn_scr('choghondar 964-92962-6-3 شلغم')[1]


def test_oclc1():
    assert oclc_scr('875039842')[1] == (
        '* {{cite book | last=Lewis | first=James Bryant | last2=Sesay | first2=Amadu | title=Korea and globalization : politics, economics and culture | publisher=RoutledgeCurzon | publication-place=Richmond | year=2002 | isbn=978-0-7007-1512-1 | oclc=875039842}}'
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
    assert ISBN_10OR13_SEARCH('2-253-00422-7')


def test_citoid_only():  # 31
    assert (
        '* {{cite book | last=Ramseier | first=Walter '
        '| title=Münchenstein - Heimatkunde | publication-place=[Liestal] '
        '| isbn=978-3-85673-522-7 | oclc=613273377 '
        '| language=de}}'
    ) == isbn_scr('3-85673-522-4')[1]


def test_invalid_oclc():
    with raises(ReturnError) as e:
        oclc_dict('99999999999999')
        assert e.args == (
            'Error processing OCLC number: 99999999999999',
            'Make sure the OCLC identifier is valid.',
            ''
        )


def test_oclc_with_issn():
    assert oclc_scr('22239204')[1] == (
        '* {{cite journal | title=73 amateur radio today | publisher=WGE Pub. | publication-place=Hancock, N.H. | year=1990 | issn=1052-2522 | oclc=22239204 | ref={{sfnref | WGE Pub. | 1990}}}}'
    )


def test_worldcat_url():
    assert worldcat_scr('https://www.worldcat.org/title/46908525')[1] == (
        '* {{cite book | last=Lewis | first=James Bryant | last2=Sesay | first2=Amadu | title=Korea and globalization : politics, economics and culture | publisher=RoutledgeCurzon | publication-place=Richmond | year=2002 | isbn=978-0-7007-1512-1 | oclc=46908525}}'
    )


def test_not_identified_pulisher():
    assert worldcat_scr('https://www.worldcat.org/title/960872319')[1] == (
        '* {{cite book | last=Loftis | first=Cory | title=Before I forget : art of Cory Loftis | year=2105 | isbn=978-0-692-57330-3 | oclc=960872319}}'
    )
    assert worldcat_scr('https://www.worldcat.org/title/650188009')[1] == (
        '* {{cite book | last=Wilde | first=Geoff | last2=Braham | first2=Michael | title=Sandgrounders : the complete league history of Southport Football Club | publisher=Carnegie | year=1995 | isbn=978-1-874181-14-9 | oclc=650188009}}'
    )
    assert worldcat_scr('https://www.worldcat.org/title/1051746391')[1] == (
        '* {{cite book | last=Love | first=James Lee | title=Recollections : written in the Library of Congress, Washington, D.C. | year=1921 | oclc=1051746391}}'
    )
