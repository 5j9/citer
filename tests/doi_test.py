from unittest.mock import patch

from httpx import HTTPError

from lib.commons import dict_to_sfn_cit_ref
from lib.doi import doi_to_dict


def doi_scr(doi) -> tuple:
    with patch('lib.doi.get_citoid_dict', side_effect=HTTPError('')):
        doi_scr = dict_to_sfn_cit_ref(doi_to_dict(doi))
    return doi_scr


def citoid_scr(doi) -> tuple:
    return dict_to_sfn_cit_ref(doi_to_dict(doi))


def test_doi1():
    assert doi_scr('https://doi.org/10.1038%2Fnrd842')[1] == (
        '* {{cite journal | last=Atkins | first=Joshua H. | '
        'last2=Gershell | first2=Leland J. | title='
        'Selective anticancer drugs | journal=Nature Reviews Drug '
        'Discovery | publisher=Springer Science and Business Media LLC '
        '| volume=1 | issue=7 '
        '| year=2002 | issn=1474-1776 | doi=10.1038/nrd842 '
        '| pages=491–492}}'
    )
    assert citoid_scr('https://doi.org/10.1038%2Fnrd842')[1] == (
        '* {{cite journal | last=Atkins | first=Joshua H. | last2=Gershell | '
        'first2=Leland J. | title=Selective anticancer drugs | journal=Nature Reviews '
        'Drug Discovery | volume=1 | issue=7 | date=2002 | issn=1474-1776 | '
        'doi=10.1038/nrd842 | pages=491–492}}'
    )


def test_doi2():
    """Title of this DOI could not be detected in an older version."""
    assert doi_scr('http://www.jstor.org/stable/info/10.1086/677379')[1] == (
        '* {{cite journal | title=Books of Critical Interest '
        '| journal=Critical Inquiry '
        '| publisher=University of Chicago Press | volume=40 '
        '| issue=3 | year=2014 | issn=0093-1896 | doi=10.1086/677379 '
        '| pages=272–281 '
        '| ref={{sfnref | University of Chicago Press | 2014}}'
        '}}'
    )
    assert citoid_scr('http://www.jstor.org/stable/info/10.1086/677379')[
        1
    ] == (
        '* {{cite journal | title=Books of Critical Interest | journal=Critical '
        'Inquiry | volume=40 | issue=3 | date=2014 | issn=0093-1896 | '
        'doi=10.1086/677379 | pages=272–281 | ref={{sfnref | Critical Inquiry | '
        '2014}}}}'
    )


def test_doi3():
    """No author. URL contains %2F."""
    assert doi_scr('https://doi.org/10.1037%2Fh0063404')[1] == (
        '* {{cite journal | last=Spitzer | first=H. F. '
        '| title=Studies in retention. '
        '| journal=Journal of Educational Psychology '
        '| publisher=American Psychological Association (APA) '
        '| volume=30 | issue=9 | year=1939 | issn=0022-0663 '
        '| doi=10.1037/h0063404 | pages=641–656}}'
    )
    assert citoid_scr('https://doi.org/10.1037%2Fh0063404')[1] == (
        '* {{cite journal | last=Spitzer | first=H. F. | title=Studies in retention. '
        '| journal=Journal of Educational Psychology | volume=30 | issue=9 | '
        'date=1939 | issn=1939-2176 | doi=10.1037/h0063404 | pages=641–656}}'
    )


def test_doi4():
    """publisher=Informa {UK"""
    assert (
        '* {{cite journal | last=Davis | first=Margaret I. | last2=Jason '
        '| first2=Leonard A. | last3=Ferrari | first3=Joseph R. '
        '| last4=Olson | first4=Bradley D. | last5=Alvarez '
        '| first5=Josefina '
        '| title=A Collaborative Action Approach to Researching Substance'
        ' Abuse Recovery '
        '| journal=The American Journal of Drug and Alcohol Abuse '
        '| publisher=Informa UK Limited '
        '| volume=31 | issue=4 | year=2005 | issn=0095-2990 '
        '| doi=10.1081/ada-200068110 | pages=537–553}}'
    ) == doi_scr('10.1081%2Fada-200068110')[1]


def test_incollection():
    """Test the `incollection` type."""
    assert doi_scr('DOI 10.1007/BFb0064872')[1] == (
        '* {{cite book '
        '| last=Meyer '
        '| first=Albert R. '
        '| title=Lecture Notes in Mathematics '
        '| chapter=Weak monadic second order theory of succesor is not'
        ' elementary-recursive '
        '| publisher=Springer Berlin Heidelberg '
        '| publication-place=Berlin, Heidelberg '
        '| year=1975 '
        '| isbn=978-3-540-07155-6 '
        '| issn=0075-8434 '
        '| doi=10.1007/bfb0064872}}'
    )
    assert citoid_scr('DOI 10.1007/BFb0064872')[1] == (
        '* {{cite book | last=Meyer | first=Albert R. | title=Logic Colloquium | '
        'chapter=Weak monadic second order theory of succesor is not '
        'elementary-recursive | publisher=Springer Berlin Heidelberg | '
        'publication-place=Berlin, Heidelberg | volume=453 | date=1975 | '
        'isbn=978-3-540-07155-6 | doi=10.1007/bfb0064872}}'
    )


def test_doi_isbn_no_year():
    """Test when issue date is empty."""
    assert doi_scr('10.3990/1.9789036526326')[1] == (
        '* {{cite thesis | last=Ambati | first=V.R. '
        '| title=Forecasting water waves and currents :'
        ' a space-time approach '
        '| publisher=University Library/University of Twente '
        '| isbn=978-90-365-2632-6 | doi=10.3990/1.9789036526326}}'
    )
    assert citoid_scr('10.3990/1.9789036526326')[1] == (
        '* {{cite thesis | degree=PhD | last=Ambati | first=V.R. | title=Forecasting '
        'water waves and currents : a space-time approach | publisher=University of '
        'Twente | publication-place=Enschede, The Netherlands | date=2007-02-08 | '
        'doi=10.3990/1.9789036526326}}'
    )


def test_conference_location():
    """Test citing a conference with location."""
    assert doi_scr('10.1145/1117278')[1] == (
        '* {{cite conference '
        '| title=Proceedings of the international workshop on System-level'
        " interconnect prediction - SLIP'06 "
        '| publisher=ACM Press '
        '| publication-place=New York, New York, USA '
        '| year=2006 '
        '| isbn=1-59593-255-0 '
        '| doi=10.1145/1117278 '
        '| ref={{sfnref | ACM Press | 2006}}'
        '}}'
    )
    assert citoid_scr('10.1145/1117278')[1] == (
        '* {{cite conference | last=Hutton | first=Mike | last2=Dambre | first2=Joni '
        '| title=Proceedings of the 2006 international workshop on System-level '
        'interconnect prediction | publisher=ACM | publication-place=Munich Germany | '
        'date=2006-03-04 | isbn=978-1-59593-255-6 | doi=10.1145/1117278}}'
    )


def test_non_numeric_volume():
    assert doi_scr('10.1109/TIM.1985.4315297')[1] == (
        '* {{cite journal | last=Niemeyer | first=Jurgen | last2=Hinken '
        '| first2=Johann H. | last3=Kautz | first3=Richard L. '
        '| title=Near-Zero Bias Arrays of Josephson Tunnel Junctions '
        'Providing Standard Voltages up to 1 V | journal=IEEE '
        'Transactions on Instrumentation and Measurement '
        '| publisher=Institute of Electrical and Electronics Engineers '
        '(IEEE) | volume=IM-34 | issue=2 | year=1985 | issn=0018-9456 '
        '| doi=10.1109/tim.1985.4315297 | pages=185–187}}'
    )
    assert citoid_scr('10.1109/TIM.1985.4315297')[1] == (
        '* {{cite journal | last=Niemeyer | first=Jurgen | last2=Hinken | '
        'first2=Johann H. | last3=Kautz | first3=Richard L. | title=Near-Zero Bias '
        'Arrays of Josephson Tunnel Junctions Providing Standard Voltages up to 1 V | '
        'journal=IEEE Transactions on Instrumentation and Measurement | volume=IM-34 '
        '| issue=2 | date=1985 | issn=0018-9456 | doi=10.1109/TIM.1985.4315297 | '
        'pages=185–187}}'
    )


def test_bad_author_name():
    assert doi_scr('10.1007/JHEP10(2017)157')[1] == (
        '* {{cite journal | last=Giusti | first=D. | last2=Lubicz '
        '| first2=V. | last3=Martinelli | first3=G. | last4=Sanfilippo '
        '| first4=F. | last5=Simula | first5=S. '
        '| title=Strange and charm HVP contributions to the muon (g − 2) '
        'including QED corrections with twisted-mass fermions '
        '| journal=Journal of High Energy Physics '
        '| publisher=Springer Science and Business Media LLC '
        '| volume=2017 | issue=10 '
        '| year=2017 | issn=1029-8479 | doi=10.1007/jhep10(2017)157}}'
    )
    assert citoid_scr('10.1007/JHEP10(2017)157')[1] == (
        '* {{cite journal | author=on behalf of ETM collaboration | last2=Giusti | '
        'first2=D. | last3=Lubicz | first3=V. | last4=Martinelli | first4=G. | '
        'last5=Sanfilippo | first5=F. | last6=Simula | first6=S. | title=Strange and '
        'charm HVP contributions to the muon (g − 2) including QED corrections with '
        'twisted-mass fermions | journal=Journal of High Energy Physics | volume=2017 '
        '| issue=10 | date=2017 | issn=1029-8479 | doi=10.1007/JHEP10(2017)157}}'
    )


def test_contains_brackets():  # 33
    assert (
        doi_scr('10.1657/1523-0430(07-512)[ZHU]2.0.CO;2')[1]
        == (  # note `[zhu]` in doi, it should not be escaped
            '* {{cite journal | last=Zhu | first=Liping | last2=Lin | first2=Xiao '
            '| last3=Li | first3=Yuanfang | last4=Li | first4=Bingyuan '
            '| last5=Xie | first5=Manping '
            '| title=Ostracoda Assemblages in Core Sediments and Their '
            'Environmental Significance in a Small Lake in Northwest Tibet, China '
            '| journal=Arctic, Antarctic, and Alpine Research '
            '| publisher=Informa UK Limited | volume=39 | issue=4 | year=2007 '
            '| issn=1523-0430 | doi=10.1657/1523-0430(07-512)[zhu]2.0.co;2 '
            '| pages=658–662}}'
        )
    )
    assert citoid_scr('10.1657/1523-0430(07-512)[ZHU]2.0.CO;2')[1] == (
        '* {{cite journal | last=Zhu | first=Liping | last2=Lin | first2=Xiao | '
        'last3=Li | first3=Yuanfang | last4=Li | first4=Bingyuan | last5=Xie | '
        'first5=Manping | title=Ostracoda Assemblages in Core Sediments and Their '
        'Environmental Significance in a Small Lake in Northwest Tibet, China | '
        'journal=Arctic, Antarctic, and Alpine Research | volume=39 | issue=4 | '
        'date=2007 | issn=1523-0430 | doi=10.1657/1523-0430(07-512)[ZHU]2.0.CO;2 | '
        'pages=658–662}}'
    )


def test_non_crossref_doi():  # 35
    assert doi_scr('10.48550/arXiv.1811.06526')[1][:-12] == (
        '* {{cite journal | last=Hein | first=Andreas M. | last2=Baxter '
        '| first2=Stephen '
        '| title=Artificial Intelligence for Interstellar Travel '
        '| journal=arXiv | publisher=arXiv | doi=10.48550/ARXIV.1811.06526 '
        '| url=https://arxiv.org/abs/1811.06526 '
        '| access-date='
    )
    # lacks required journal parameter
    assert citoid_scr('10.48550/arXiv.1811.06526')[1] == (
        '* {{cite journal | last=Hein | first=Andreas M. | last2=Baxter | '
        'first2=Stephen | title=Artificial Intelligence for Interstellar Travel | '
        'date=2018 | doi=10.48550/ARXIV.1811.06526}}'
    )


def test_doi_with_full_date():  # 36
    assert doi_scr('10.1029/2002GL014729')[1] == (
        '* {{cite journal | last=Webber | first=W. R. | last2=McDonald '
        '| first2=F. B. | last3=Lockwood | first3=J. A. | last4=Heikkila '
        '| first4=B. '
        '| title=The effect of the July 14, 2000 “Bastille Day” solar flare '
        'event on &gt;70 MeV galactic cosmic rays observed at V1 and V2 in '
        'the distant heliosphere | journal=Geophysical Research Letters '
        '| publisher=American Geophysical Union (AGU) | volume=29 '
        '| issue=10 | date=2002-05-15 | issn=0094-8276 '
        '| doi=10.1029/2002gl014729 | pages=15–1–15–3}}'
    )
    assert citoid_scr('10.1029/2002GL014729')[1] == (
        '* {{cite journal | last=Webber | first=W. R. | last2=McDonald | first2=F. B. '
        '| last3=Lockwood | first3=J. A. | last4=Heikkila | first4=B. | title=The '
        'effect of the July 14, 2000 “Bastille Day” solar flare event on >70 MeV '
        'galactic cosmic rays observed at V1 and V2 in the distant heliosphere | '
        'journal=Geophysical Research Letters | volume=29 | issue=10 | '
        'date=2002-05-15 | issn=0094-8276 | doi=10.1029/2002GL014729}}'
    )


def test_sfn_extract_year_from_date():
    s, c, r = doi_scr('10.1073/pnas.2015159118')
    assert s == '{{sfn | Almeida | Viala | Nachtigall | Broe | 2021 | p=}}'
    assert (
        c
        == '* {{cite journal | last=Almeida | first=Diego Dantas | last2=Viala | first2=Vincent Louis | last3=Nachtigall | first3=Pedro Gabriel | last4=Broe | first4=Michael | last5=Gibbs | first5=H. Lisle | last6=Serrano | first6=Solange Maria de Toledo | last7=Moura-da-Silva | first7=Ana Maria | last8=Ho | first8=Paulo Lee | last9=Nishiyama-Jr | first9=Milton Yutaka | last10=Junqueira-de-Azevedo | first10=Inácio L. M. | title=Tracking the recruitment and evolution of snake toxins using the evolutionary context provided by the <i>Bothrops jararaca</i> genome | journal=Proceedings of the National Academy of Sciences | publisher=Proceedings of the National Academy of Sciences | volume=118 | issue=20 | date=2021-05-10 | issn=0027-8424 | doi=10.1073/pnas.2015159118}}'
    )
    s, c, r = citoid_scr('10.1073/pnas.2015159118')
    assert s == '{{sfn | Almeida | Viala | Nachtigall | Broe | 2021 | p=}}'
    assert c == (
        '* {{cite journal | last=Almeida | first=Diego Dantas | last2=Viala | '
        'first2=Vincent Louis | last3=Nachtigall | first3=Pedro Gabriel | last4=Broe '
        '| first4=Michael | last5=Gibbs | first5=H. Lisle | last6=Serrano | '
        'first6=Solange Maria de Toledo | last7=Moura-da-Silva | first7=Ana Maria | '
        'last8=Ho | first8=Paulo Lee | last9=Nishiyama-Jr | first9=Milton Yutaka | '
        'last10=Junqueira-de-Azevedo | first10=Inácio L. M. | title=Tracking the '
        'recruitment and evolution of snake toxins using the evolutionary context '
        'provided by the Bothrops jararaca genome | journal=Proceedings of the '
        'National Academy of Sciences | volume=118 | issue=20 | date=2021-05-18 | '
        'issn=0027-8424 | pmid=33972420 | pmc=PMC8157943 | '
        'doi=10.1073/pnas.2015159118}}'
    )


def test_doi_without_date():  # 46
    assert doi_scr('10.1023/a:1018715525493')[1] == (
        '* {{cite journal | last=Sigusch | first=Volkmar | title= | journal=Archives '
        'of Sexual Behavior | publisher=Springer Science and Business Media LLC | '
        'volume=27 | issue=4 | year=1998 | issn=0004-0002 | '
        'doi=10.1023/a:1018715525493 | pages=331–359}}'
    )
    assert citoid_scr('10.1023/a:1018715525493')[1] == (
        '* {{cite journal | last=Sigusch | first=Volkmar | title=[No title found] | '
        'journal=Archives of Sexual Behavior | volume=27 | issue=4 | date=1998 | '
        'doi=10.1023/A:1018715525493 | pages=331–359}}'
    )
