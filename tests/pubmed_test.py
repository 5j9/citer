from unittest.mock import Mock, patch

from curl_cffi import CurlError

from lib import pubmed
from lib.commons import data_to_sfn_cit_ref
from lib.pubmed import pmcid_data, pmid_data


def pmid_scr(id_, date_format='%Y-%m-%d'):
    return data_to_sfn_cit_ref(pmid_data(id_), date_format)


def pmcid_scr(id_, date_format='%Y-%m-%d'):
    return data_to_sfn_cit_ref(pmcid_data(id_), date_format)


def test_doi_update():
    """Updated using doi."""
    with patch('lib.pubmed.citoid_data', side_effect=CurlError):
        assert (
            pmcid_scr('3538472')[1]
            == '* {{cite journal | last=Sweetser | first=Seth | title=Evaluating the Patient With Diarrhea: A Case-Based Approach | journal=Mayo Clinic Proceedings | publisher=Elsevier BV | volume=87 | issue=6 | year=2012 | issn=0025-6196 | pmid=22677080 | pmc=3538472 | doi=10.1016/j.mayocp.2012.02.015 | pages=596–602}}'
        )
    assert (
        pmcid_scr('3538472')[1]
        == '* {{cite journal | last=Sweetser | first=Seth | title=Evaluating the Patient With Diarrhea: A Case-Based Approach | journal=Mayo Clinic Proceedings | volume=87 | issue=6 | date=2012 | issn=0025-6196 | pmid=22677080 | pmc=3538472 | doi=10.1016/j.mayocp.2012.02.015 | pages=596–602}}'
    )


def test_spanish_no_doi():
    """Test retrieval without doi."""
    with patch('lib.pubmed.citoid_data', side_effect=CurlError):
        assert pmid_scr('123455')[1] == (
            '* {{cite journal | last=Mendozo Hernández | first=P | title=[Clinical '
            'diagnosis and therapy. Intravenous and oral rehydration]. | journal=Boletin '
            'de la Oficina Sanitaria Panamericana. Pan American Sanitary Bureau | '
            'volume=78 | issue=4 | year=1975 | issn=0030-0632 | pmid=123455 | '
            'pages=307–17 | language=es}}'
        )
    assert pmid_scr('123455')[1] == (
        '* {{cite journal | last=Mendozo Hernández | first=P. | title=[Clinical '
        'diagnosis and therapy. Intravenous and oral rehydration] | journal=Boletin '
        'De La Oficina Sanitaria Panamericana. Pan American Sanitary Bureau | '
        'volume=78 | issue=4 | date=1975 | issn=0030-0632 | pmid=123455 | '
        'pages=307–317}}'
    )


@patch.object(pubmed, 'crossref_update', Mock(return_value=None))
def test_has_doi_but_no_crossref():
    """Test while doi exists but crossref_update is disabled."""
    with patch('lib.pubmed.citoid_data', side_effect=CurlError):
        assert pmcid_scr('2562006', '%d %B %Y')[1] == (
            '* {{cite journal | last=Bannen | first=RM | last2=Suresh | first2=V | '
            'last3=Phillips | first3=GN Jr | last4=Wright | first4=SJ | last5=Mitchell | '
            'first5=JC | title=Optimal design of thermally stable proteins | '
            'journal=Bioinformatics | volume=24 | issue=20 | date=22 August 2008 | '
            'pmid=18723523 | pmc=2562006 | doi=10.1093/bioinformatics/btn450 | '
            'pages=2339–2343}}'
        )
    assert pmcid_scr('2562006', '%d %B %Y')[1] == (
        '* {{cite journal | last=Bannen | first=Ryan M. | last2=Suresh | '
        'first2=Vanitha | last3=Phillips | first3=George N. | last4=Wright | '
        'first4=Stephen J. | last5=Mitchell | first5=Julie C. | title=Optimal design '
        'of thermally stable proteins | journal=Bioinformatics | volume=24 | issue=20 '
        '| date=15 October 2008 | issn=1367-4803 | pmid=18723523 | pmc=2562006 | '
        'doi=10.1093/bioinformatics/btn450 | pages=2339–2343}}'
    )
