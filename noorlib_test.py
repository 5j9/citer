#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test noorlib.py module."""


import unittest

import dummy_requests
import noorlib
from noorlib import noorlib_response


class NoorlibTest(unittest.TestCase):

    def test_nl1(self):
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18879'
        o = noorlib_response(i)
        e = (
            '* {{cite book '
            '| last=مرتضی زبیدی '
            '| first=محمد بن محمد '
            '| last2=شیری '
            '| first2=علی '
            '| title=تاج العروس من جواهر القاموس '
            '| publisher=دار الفکر '
            '| location=بيروت '
            '| series=تاج العروس من جواهر القاموس '
            '| volume=10 '
            '| url=http://www.noorlib.ir/View/fa/Book/BookView/Image/18879 '
            '| language=عربی '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(e, o.cite)

    def test_nl2(self):
        """The year parameter is not present."""
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18454'
        o = noorlib_response(i)
        er = '{{sfn | کورانی}}'
        ec = (
            '* {{cite book '
            '| last=کورانی '
            '| first=علی '
            '| title=المعجم الموضوعی لاحادیث الامام الم'
            'هدی عجل الله تعالی فرجه الشریف '
            '| publisher=دار المرتضی '
            '| location=بيروت '
            '| series=المعجم الموضوعی لاحادیث الامام المهدی'
            ' عجل الله تعالی فرجه الشریف '
            '| volume=1 '
            '| url=http://www.noorlib.ir/View/fa/Book/BookView/Image/18454 '
            '| language=عربی '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(er, o.sfn)
        self.assertIn(ec, o.cite)


noorlib.requests_get = dummy_requests.DummyRequests().get
if __name__ == '__main__':
    unittest.main()
