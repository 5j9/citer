#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test noormags.py module."""


import unittest

import dummy_requests
import noormags
from noormags import noormags_response


class NoormagsTest(unittest.TestCase):

    def test_nm1(self):
        i = 'http://www.noormags.com/view/fa/articlepage/5798/102/Text'
        o = noormags_response(i)
        e = (
            '* {{cite journal '
            '| last=موسوی '
            '| first=زهرا '
            '| title=مقرنس در معماری '
            '| journal=کتاب ماه هنر '
            '| issue=45 '
            '| year=2002 '
            '| pages=102–106 '
            '| url=http://www.noormags.ir/view/fa/articlepage/104040 '
            '| language=fa '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(e, o.cite)

    def test_nm2(self):
        """The second author does not have a last name. (Bibtex file error)"""
        i = 'http://www.noormags.ir/view/fa/articlepage/261461'
        o = noormags_response(i)
        e = (
            '* {{cite journal '
            '| last=ایرانی '
            '| first=هوشنگ '
            '| last2=ولف '
            '| first2=آ. '
            '| title=لوژیستیک '
            '| journal=دانش '
            '| issue=6 '
            '| year=1949 '
            '| pages=316–324 '
            '| url=http://www.noormags.ir/view/fa/articlepage/261461 '
            '| language=fa '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(e, o.cite)

    def test_nm3(self):
        """Reftag check."""
        i = (
            'http://www.noormags.ir/view/fa/articlepage/'
            '692447?sta=%D8%AF%D8%B9%D8%A7%DB%8C%20%D8%A7%D8%A8%D9%88%D8%AD%'
            'D9%85%D8%B2%D9%87%20%D8%AB%D9%85%D8%A7%D9%84%DB%8C'
        )
        o = noormags_response(i)
        sfnt = '{{sfn | سلیمانی میمند | 2010 | pp=103–124}}'
        ctnt = (
            '* {{cite journal '
            '| last=سلیمانی میمند '
            '| first=مریم '
            '| title=بررسی فضایل قرآنی در دعای ابوحمزه ثمالی '
            '| journal=بینات '
            '| issue=68 '
            '| year=2010 '
            '| pages=103–124 '
            '| url=http://www.noormags.ir/view/fa/articlepage/692447 '
            '| language=fa '
            '| ref=harv '
            '| accessdate='
        )
        rftg = (
            '<ref name="سلیمانی میمند 2010 pp. 103–124">'
            '{{cite journal '
            '| last=سلیمانی میمند '
            '| first=مریم '
            '| title=بررسی فضایل قرآنی در دعای ابوحمزه ثمالی '
            '| journal=بینات '
            '| issue=68 '
            '| year=2010 '
            '| pages=103–124 '
            '| url=http://www.noormags.ir/view/fa/articlepage/692447 '
            '| language=fa '
            '| accessdate='
        )
        self.assertIn(sfnt, o.sfn)
        self.assertIn(ctnt, o.cite)
        self.assertIn(rftg, o.ref)


noormags.requests_get = dummy_requests.DummyRequests().get
if __name__ == '__main__':
    unittest.main()
