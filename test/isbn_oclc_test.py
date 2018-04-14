#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test isbn.py module."""


import unittest

from test import dummy_requests
from src import isbn_oclc
from src.isbn_oclc import isbn_sfn_cit_ref, oclc_sfn_cit_ref


class IsbnTest(unittest.TestCase):

    def test_is1(self):
        """not found in adinebook"""
        self.assertIn((
            '* {{cite book '
            '| last=Adkins '
            '| first=Roy '
            '| title=The war for all the oceans : '
            'from Nelson at the Nile to Napoleon at Waterloo '
            '| publisher=Abacus '
            '| publication-place=London '
            '| year=2007 '
            '| isbn=978-0-349-11916-8 '
            '| oclc=137313052 '
            '| ref=harv}}'
        ), isbn_sfn_cit_ref('9780349119168', pure=True)[1])

    def test_is2(self):
        """not found in ottobib"""
        self.assertIn((
            '* {{cite book '
            '| others=بدیل بن علی خاقانی (شاعر),  جهانگیر منصور (به اهتمام),'
            ' and  بدیع الزمان فروزانفر (مقدمه) '
            '| title=دیوان خاقانی شروانی '
            '| publisher=نگاه '
            '| year=1389 '
            '| isbn=978-964-6736-71-9 '
            '| language=fa '
            '| ref={{sfnref | نگاه | 1389}}'
        ), isbn_sfn_cit_ref('978-964-6736-71-9', pure=True)[1])

    def test_is3(self):
        """exists in both"""
        self.assertIn((
            '* {{cite book '
            '| others=سحر معصومی (به اهتمام) '
            '| title=راز گل سرخ: نقد و گزیده شعرهای سهراب سپهری '
            '| publisher=نگاه '
            '| year=1386 '
            '| isbn=964-6736-34-3 '
            '| oclc=53446327 '
            '| language=fa '
            '| ref={{sfnref | نگاه | 1386}}'
        ), isbn_sfn_cit_ref('964-6736-34-3 ')[1])

    def test_is4(self):
        """unpure isbn10 not found in ottobib"""
        self.assertIn((
            '* {{cite book '
            '| last=حافظ '
            '| first=شمس الدین محمد '
            '| others= رضا نظرزاده (به اهتمام) '
            '| title=دیوان کامل حافظ همراه با فالنامه '
            '| publisher=دیوان '
            '| year=1385 '
            '| isbn=964-92962-6-3 '
            '| language=fa '
            '| ref=harv'
        ), isbn_sfn_cit_ref('choghondar 964-92962-6-3 شلغم')[1])


class OCLCTest(unittest.TestCase):

    def test_oclc1(self):
        self.assertEqual((
            '* {{cite book '
            '| last=Lewis '
            '| first=James Bryant. '
            '| last2=Sesay '
            '| first2=Amadu. '
            '| title=Korea and globalization :'
            ' politics, economics and culture '
            '| publisher=RoutledgeCurzon '
            '| year=2002 '
            '| oclc=875039842 '
            '| ref=harv}}'
        ), oclc_sfn_cit_ref('875039842')[1])


isbn_oclc.requests_get = dummy_requests.DummyRequests().get
if __name__ == '__main__':
    unittest.main()
