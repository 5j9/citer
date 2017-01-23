#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test googlebooks.py module."""


import unittest

import dummy_requests
import googlebooks
from googlebooks import GoogleBooksResponse


class GooglebooksTest(unittest.TestCase):

    def test_gb1(self):
        i = (
            'http://books.google.com/books?'
            'id=pzmt3pcBuGYC&pg=PR11&lpg=PP1&dq=digital+library'
        )
        o = GoogleBooksResponse(i)
        e = (
            '* {{cite book '
            '| last=Arms '
            '| first=W.Y. '
            '| title=Digital Libraries '
            '| publisher=MIT Press '
            '| series=Digital libraries and electronic publishing '
            '| year=2000 '
            '| isbn=978-0-262-26134-0 '
            '| url=http://books.google.com/books?id=pzmt3pcBuGYC&pg=PR11 '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(e, o.cite)

    def test_gb2(self):
        """a book with more than 4 authors (10 authors)"""
        i = (
            'http://books.google.com/books?'
            'id=U46IzqYLZvAC&pg=PT57#v=onepage&q&f=false'
        )
        o = GoogleBooksResponse(i)
        e1 = (
            '{{sfn '
            '| Anderson '
            '| DeBolt '
            '| Featherstone '
            '| Gunther '
            '| 2010 '
            '| p=57}}'
        )
        e2 = (
            '* {{cite book '
            '| last=Anderson '
            '| first=E. '
            '| last2=DeBolt '
            '| first2=V. '
            '| last3=Featherstone '
            '| first3=D. '
            '| last4=Gunther '
            '| first4=L. '
            '| last5=Jacobs '
            '| first5=D.R. '
            '| last6=Mills '
            '| first6=C. '
            '| last7=Schmitt '
            '| first7=C. '
            '| last8=Sims '
            '| first8=G. '
            '| last9=Walter '
            '| first9=A. '
            '| last10=Jensen-Inman '
            '| first10=L. '
            '| title=InterACT with Web Standards: '
            'A holistic approach to web design '
            '| publisher=Pearson Education '
            '| year=2010 '
            '| isbn=978-0-13-270490-8 '
            '| url=http://books.google.com/books?id=U46IzqYLZvAC&pg=PT57 '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(e1, o.sfn)
        self.assertIn(e2, o.cite)

    def test_gb3(self):
        """Non-ascii characters in title (Some of them where removed later)"""
        i = (
            'http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588&dq=%22a+'
            'Delimiter+is%22&hl=en&sa=X&ei=oNKSUrKeDovItAbO_4CoBA&ved='
            '0CC4Q6AEwAA#v=onepage&q=%22a%20Delimiter%20is%22&f=false'
        )
        o = GoogleBooksResponse(i)
        e1 = '{{sfn | Farrell | 2009 | p=588}}'
        e2 = (
            '* {{cite book '
            '| last=Farrell '
            '| first=J. '
            '| title=Microsoft Visual C# 2008 Comprehensive: '
            'An Introduction to Object-Oriented Programming '
            '| publisher=Cengage Learning '
            '| year=2009 '
            '| isbn=978-1-111-78619-9 '
            '| url=http://books.google.com/books?id=icMEAAAAQBAJ&pg=PA588 '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(e1, o.sfn)
        self.assertIn(e2, o.cite)

    def test_gb4(self):
        """Non-ascii characters in author's name."""
        i = (
            'http://books.google.com/books?id='
            'i8nZjjo_9ikC&pg=PA229&dq=%22legal+translation+is%22&hl=en&sa='
            'X&ei=hEuYUr_mOsnKswb49oDQCA&ved=0CC4Q6AEwAA#v=onepage&q='
            '%22legal%20translation%20is%22&f=false'
        )
        o = GoogleBooksResponse(i)
        e1 = '{{sfn | Šarčević | 1997 | p=229}}'
        e2 = (
            '* {{cite book '
            '| last=Šarčević '
            '| first=S. '
            '| title=New Approach to Legal Translation '
            '| publisher=Kluwer Law International '
            '| year=1997 '
            '| isbn=978-90-411-0401-4 '
            '| url=http://books.google.com/books?id=i8nZjjo_9ikC&pg=PA229 '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(e1, o.sfn)
        self.assertIn(e2, o.cite)

    def test_gb5(self):
        """ref checking"""
        i = (
            'https://encrypted.google.com/books?id=6upvonUt0O8C&pg=PA378&'
            'dq=density+of+granite&hl=en&sa=X&ei=YBHIU-qCBIyX0QXusoDgAg&ved='
            '0CEIQ6AEwBjgK#v=onepage&q=density%20of%20granite&f=false'
        )
        o = GoogleBooksResponse(i)
        ctnt = (
            '* {{cite book '
            '| last=Serway '
            '| first=R. '
            '| last2=Jewett '
            '| first2=J. '
            '| title=Physics for Scientists and Engineers, Volume 1, '
            'Chapters 1-22 | publisher=Cengage Learning '
            '| series=Physics for Scientists and Engineers '
            '| year=2009 '
            '| isbn=978-1-4390-4838-2 '
            '| url=http://encrypted.google.com/books?id=6upvonUt0O8C&pg=PA378 '
            '| ref=harv '
            '| accessdate='
        )
        reft = (
            '<ref name="Serway Jewett 2009 p. 378">'
            '{{cite book '
            '| last=Serway '
            '| first=R. '
            '| last2=Jewett '
            '| first2=J. '
            '| title=Physics for Scientists and Engineers, Volume 1, '
            'Chapters 1-22 | publisher=Cengage Learning '
            '| series=Physics for Scientists and Engineers '
            '| year=2009 '
            '| isbn=978-1-4390-4838-2 '
            '| url=http://encrypted.google.com/books?id=6upvonUt0O8C&pg=PA378 '
            '| accessdate='
        )
        self.assertIn(ctnt, o.cite)
        self.assertIn(reft, o.ref)
        self.assertIn(' | page=378}}</ref>', o.ref)


googlebooks.requests_get = dummy_requests.DummyRequests().get
if __name__ == '__main__':
    unittest.main()
