#!/data/project/yadkard/venv/bin/python3.2
# -*- coding: utf-8 -*-

"""Test noorlib.py module."""


import unittest

import noorlib


class NoorlibTest(unittest.TestCase):

    def test_nl1(self):
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18879'
        o = noorlib.Citation(i)
        e = '* {{cite book|last=مرتضی زبیدی|first=محمد بن محمد|last2=شیری|first2=علی|title=تاج العروس من جواهر القاموس|publisher=دار الفکر|location=بيروت|series=تاج العروس من جواهر القاموس|volume=10|year=|url=http://www.noorlib.ir/View/fa/Book/BookView/Image/18879|language=عربی|ref=harv|accessdate='
        self.assertIn(e, o.cite)


if __name__ == '__main__':
    unittest.main()
