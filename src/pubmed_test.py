#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test noormags.py module."""


import unittest
from unittest.mock import patch, Mock

from src import dummy_requests, pubmed
from src.pubmed import pmid_sfn_cit_ref, pmcid_sfn_cit_ref


class PMCID(unittest.TestCase):

    """Test pmcid_sfn_cit_ref."""

    def test_doi_update(self):
        """Updated using doi."""
        self.assertIn(
            '* {{cite journal '
            '| last=Sweetser '
            '| first=Seth '
            '| title=Evaluating the Patient With Diarrhea:'
            ' A Case-Based Approach '
            '| journal=Mayo Clinic Proceedings '
            '| publisher=Elsevier BV '
            '| volume=87 '
            '| issue=6 '
            '| year=2012 '
            '| issn=0025-6196 '
            '| pmid=22677080 '
            '| pmc=3538472 '
            '| doi=10.1016/j.mayocp.2012.02.015 '
            '| pages=596–602 '
            '| ref=harv}}',
            pmcid_sfn_cit_ref('3538472')[1],
        )

    def test_spanish_no_doi(self):
        """Test retrieval without doi."""
        self.assertIn(
            '* {{cite journal | last=Mendozo Hernández | first=P '
            '| title=&amp;#91;Clinical diagnosis and therapy.'
            ' Intravenous and oral rehydration&amp;#93;. '
            '| journal=Boletin de la Oficina Sanitaria Panamericana.'
            ' Pan American Sanitary Bureau | volume=78 | issue=4 | year=1975 '
            '| issn=0030-0632 | pmid=123455 | pages=307–17 | language=es '
            '| ref=harv}}',
            pmid_sfn_cit_ref('123455')[1],
        )

    @patch.object(pubmed, 'crossref_update', Mock(return_value=None))
    def test_has_doi_but_no_crossref(self):
        """Test while doi exists but crossref_update is disabled."""
        self.assertIn(
            '* {{cite journal | last=Bannen | first=RM | last2=Suresh '
            '| first2=V | last3=Phillips | first3=GN Jr | last4=Wright '
            '| first4=SJ | last5=Mitchell | first5=JC '
            '| title=Optimal design of thermally stable proteins '
            '| journal=Bioinformatics | volume=24 | issue=20 '
            '| date=22 August 2008 | pmid=18723523 | pmc=2562006 '
            '| doi=10.1093/bioinformatics/btn450 | pages=2339–2343 '
            '| ref=harv}}',
            pmcid_sfn_cit_ref('2562006', '%d %B %Y')[1],
        )


pubmed.requests_get = dummy_requests.DummyRequests().get
if __name__ == '__main__':
    unittest.main()
