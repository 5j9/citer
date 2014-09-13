#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test noormags.py module."""


import unittest
import sys

import dummy_requests
sys.path.append('..')
import noormags


class NoormagsTest(unittest.TestCase):

    def test_nm1(self):
        i = 'http://www.noormags.com/view/fa/articlepage/5798/102/Text'
        o = noormags.Response(i)
        e = '* {{cite journal|last=موسوی|first=زهرا|title=مقرنس در معماری|journal=کتاب ماه هنر|issue=45|year=1381|pages=102–106|url=http://www.noormags.com/view/fa/articlepage/104040|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.ctnt)

    def test_nm2(self):
        """The second author does not have a last name. (Bibtex file error)"""
        i = 'http://www.noormags.com/view/fa/articlepage/261461'
        o = noormags.Response(i)
        e = '* {{cite journal|last=ایرانی|first=هوشنگ|author2=آ. ولف|title=لوژیستیک|journal=دانش|issue=6|year=1328|pages=316–324|url=http://www.noormags.com/view/fa/articlepage/261461|language=fa|ref=harv|accessdate='
        self.assertIn(e, o.ctnt)

    def test_nm3(self):
        """Reftag check."""
        i = 'http://www.noormags.com/view/fa/articlepage/692447?sta=%D8%AF%D8%B9%D8%A7%DB%8C%20%D8%A7%D8%A8%D9%88%D8%AD%D9%85%D8%B2%D9%87%20%D8%AB%D9%85%D8%A7%D9%84%DB%8C'
        o = noormags.Response(i)
        sfnt = '{{sfn|سلیمانی میمند|1389|pp=103–124}}'
        ctnt = '* {{cite journal|last=سلیمانی میمند|first=مریم|title=بررسی فضایل قرآنی در دعای ابوحمزه ثمالی|journal=بینات|issue=68|year=1389|pages=103–124|url=http://www.noormags.com/view/fa/articlepage/692447|language=fa|ref=harv|accessdate='
        rftg = '<ref name="سلیمانی میمند 1389 pp. 103–124">{{cite journal|last=سلیمانی میمند|first=مریم|title=بررسی فضایل قرآنی در دعای ابوحمزه ثمالی|journal=بینات|issue=68|year=1389|pages=103–124|url=http://www.noormags.com/view/fa/articlepage/692447|language=fa|accessdate='
        self.assertIn(sfnt, o.sfnt)
        self.assertIn(ctnt, o.ctnt)
        self.assertIn(rftg, o.reft)


noormags.requests = dummy_requests.DummyRequests()
if __name__ == '__main__':
    unittest.main()
