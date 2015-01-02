#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test doi.py module."""


import unittest
import sys

sys.path.append('..')
import doi
import dummy_requests


class DoiTest(unittest.TestCase):

    def test_doi1(self):
        i = 'http://dx.doi.org/10.1038/nrd842'
        o = doi.Response(i)
        e = "* {{cite journal | last=Atkins | first=Joshua H. | last2=Gershell | first2=Leland J. | title=From the analyst's couch: Selective anticancer drugs | journal=Nature Reviews Drug Discovery | publisher=Nature Publishing Group | volume=1 | issue=7 | year=2002 | pages=491–492 | url=http://dx.doi.org/10.1038/nrd842 | doi=10.1038/nrd842 | ref=harv | accessdate="
        self.assertIn(e, o.ctnt)

    def test_doi2(self):
        """Title of this DOI could not be detected in an older version."""
        i = 'http://www.jstor.org/stable/info/10.1086/677379'
        o = doi.Response(i)
        e = '* {{cite journal | title=Books of Critical Interest | journal=Critical Inquiry | publisher=University of Chicago Press | volume=40 | issue=3 | year=2014 | pages=272–281 | url=http://dx.doi.org/10.1086/677379 | doi=10.1086/677379 | ref={{sfnref | University of Chicago Press | 2014}} | accessdate='
        self.assertIn(e, o.ctnt)

    def test_doi3(self):
        """No author. URL contains %2F."""
        i = 'http://dx.doi.org/10.1037%2Fh0063404'
        o = doi.Response(i)
        e = '* {{cite journal | last=Spitzer | first=H. F. | title=Studies in retention. | journal=Journal of Educational Psychology | publisher=American Psychological Association (APA) | volume=30 | issue=9 | year=1939 | pages=641–656 | url=http://dx.doi.org/10.1037/h0063404 | doi=10.1037/h0063404 | ref=harv | accessdate='
        self.assertIn(e, o.ctnt)


doi.requests = dummy_requests.DummyRequests()
if __name__ == '__main__':
    unittest.main()
