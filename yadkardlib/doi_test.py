#!/data/project/yadkard/venv/bin/python
# -*- coding: utf-8 -*-

"""Test doi.py module."""


import unittest

import doi


class DoiTest(unittest.TestCase):

    def test_doi1(self):
        i = 'http://dx.doi.org/10.1038/nrd842'
        o = doi.Citation(i)
        e = u"* {{cite journal|last=Atkins|first=Joshua H.|last2=Gershell|first2=Leland J.|title=From the analyst's couch: Selective anticancer drugs|journal=Nature Reviews Drug Discovery|publisher=Nature Publishing Group|volume=1|issue=7|pages=491\u2013492|url=http://dx.doi.org/10.1038/nrd842|doi=10.1038/nrd842|ref=harv|accessdate="
        self.assertIn(e, o.cite)

    def test_doi2(self):
        '''DOI with unsafe characters (<>)

Warning: this test fials a lot due to "HTTPError: HTTP Error 500: Internal
Server Error". Also be aware that there was an &amp; entity which was manually substitute in
expected output
'''
        i = '10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5'
        o = doi.Citation(i, pure = True)
        e = u"* {{cite journal|last=Dian|first=Noor Lida Habi Mat|last2=Sudin|first2=Nor'aini|last3=Yusoff|first3=Mohd Suria Affandi|title=Characteristics of Microencapsulated Palm-Based Oil as Affected by Type of Wall Material|journal=Journal of the Science of Food and Agriculture|publisher=Wiley-Blackwell|volume=70|issue=4|pages=422\u2013426|url=http://dx.doi.org/10.1002/(SICI)1097-0010(199604)70:4<422::AID-JSFA514>3.0.CO;2-5|doi=10.1002/(sici)1097-0010(199604)70:4<422::aid-jsfa514>3.0.co;2-5|ref=harv|accessdate="
        self.assertIn(e, o.cite)

    def test_doi3(self):
        """Title of this DOI could not be detected in an older version."""
        i = 'http://www.jstor.org/stable/info/10.1086/677379'
        o = doi.Citation(i)
        e = u'* {{cite journal|title=Books of Critical Interest|journal=Critical Inquiry|publisher=University of Chicago Press|volume=40|issue=3|pages=272–281|url=http://dx.doi.org/10.1086/677379|doi=10.1086/677379|ref={{sfnref|University of Chicago Press}}|accessdate='
        self.assertIn(e, o.cite)


if __name__ == '__main__':
    unittest.main()
