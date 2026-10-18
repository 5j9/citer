from lib.citoid import jstor_data
from lib.commons import data_to_sfn_cit_ref


def jstor_scr(*args):
    return data_to_sfn_cit_ref(jstor_data(*args))


def test_1():
    s, c, r = jstor_scr('https://www.jstor.org/stable/30078788')
    assert s == '{{sfn|Lloyd|1831|pp=171–177}}'
    assert c[: c.index('| access-date=')] == (
        '* {{cite journal | last=Lloyd | first=Humphrey '
        '| title=On a New Case of Interference of the Rays of Light '
        '| journal=The Transactions of the Royal Irish Academy '
        '| publisher=Royal Irish Academy | volume=17 | date=1831 '
        '| issn=0790-8113 | jstor=30078788 | pages=171–177 '
        '| url=https://www.jstor.org/stable/30078788 '
    )


def test_2():
    s, c, r = jstor_scr(
        'https://www.jstor.org/stable/resrep26363.7?Search=yes&resultItemClick=true&searchText=google&searchUri=%2Faction%2FdoBasicSearch%3FQuery%3Dgoogle%26acc%3Doff%26wc%3Don%26fc%3Doff%26group%3Dnone%26refreqid%3Dsearch%253A2e627536469ca8786b576957a9797d56&ab_segments=0%2Fbasic_search_gsv2%2Fcontrol&refreqid=fastly-default%3Af90c911269c590baf37330b9d16ae1cd&seq=1#metadata_info_tab_contents'
    )
    assert c[: c.index('| access-date=')] == (
        '* {{cite report | last1=Singh | first1=Spandana | last2=Blase '
        '| first2=Margerite '
        '| title=Google '
        '| date=2020 | jstor=resrep26363.7 '
        '| url=https://www.jstor.org/stable/resrep26363.7 '
    )


def test_encoding():  # 25
    s, c, r = jstor_scr('https://www.jstor.org/stable/40991855')
    assert c[: c.index('| access-date=')] == (
        '* {{cite journal '
        '| last=de Figueiredo Monteiro | first=Carlos Augusto '
        '| title="Calamidades Meteorológicas no Brasil Meridional, em Agôsto de 1965" '
        '| journal=Revista Geográfica | publisher=Pan American Institute of Geography and History '
        '| volume=35 | issue=63 | date=1965 | issn=0031-0581 | jstor=40991855 '
        '| pages=173–178 | url=https://www.jstor.org/stable/40991855 '
    )


def test_issn_eissn():
    s, c, r = jstor_scr('https://www.jstor.org/stable/1687467')
    assert c[: c.index('| access-date=')] == (
        '* {{cite journal | last1=Kernighan | first1=Brian W. | last2=Morgan | '
        'first2=Samuel P. | title=The UNIX Operating System: A Model for Software '
        'Design | journal=Science | publisher=American Association for the '
        'Advancement of Science | volume=215 | issue=4534 | date=1982 | '
        'issn=0036-8075 | jstor=1687467 | pages=779–783 | '
        'url=https://www.jstor.org/stable/1687467 '
    )
