#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test urls.py module."""


import unittest

import dummy_requests
import urls
from waybackmachine import waybackmachine_response


class WaybackmachineResponse(unittest.TestCase):

    def test_live_og_link(self):
        """dead-link=no"""
        i = (
            'http://web.archive.org/web/20131021230444/'
            'http://www.huffingtonpost.com/2013/10/19/'
            'plastic-surgery-justin-bieber-100k_n_4128563.html?'
            'utm_hp_ref=mostpopular'
        )
        o = waybackmachine_response(i)
        ct = (
            '* {{cite web '
            '| author=The Huffington Post '
            '| title=LOOK: Bieber Fan Had $100K Worth Of Plastic Surgery To '
            'Look Like His Idol '
            '| website=The Huffington Post '
            '| date=2013-10-19 '
            '| url=http://www.huffingtonpost.com/2013/10/19/'
            'plastic-surgery-justin-bieber-100k_n_4128563.html?'
            'utm_hp_ref=mostpopular '
            '| archive-url=http://web.archive.org/web/20131021230444/'
            'http://www.huffingtonpost.com/2013/10/19/'
            'plastic-surgery-justin-bieber-100k_n_4128563.html?'
            'utm_hp_ref=mostpopular '
            '| archive-date=2013-10-21 '
            '| dead-url=no '
            '| ref=harv '
            '| accessdate='
        )
        self.assertIn(ct, o.cite)

    def test_dead_url(self):
        """dead-url=yes"""
        i = (
            'https://web.archive.org/web/20070429193849id_/'
            'http://www.londondevelopmentcentre.org/page.php?s=1&p=2462'
        )
        o = waybackmachine_response(i)
        ct = (
            '* {{cite web '
            '| title=London Development Centre: Support, time, recovery (STR) '
            'workers '
            '| website=londondevelopmentcentre.org '
            '| date=2007-04-29 '
            '| url=http://www.londondevelopmentcentre.org/page.php?s=1&p=2462 '
            '| archive-url=https://web.archive.org/web/20070429193849id_/'
            'http://www.londondevelopmentcentre.org/page.php?s=1&p=2462 '
            '| archive-date=2007-04-29 '
            '| dead-url=yes '
            '| ref={{sfnref | londondevelopmentcentre.org | 2007}} '
            '| accessdate='
        )
        self.assertIn(ct, o.cite)

    def test_webless_url(self):
        """The 'web/ component of the url can be omitted sometimes."""
        o = waybackmachine_response(
            'https://web.archive.org/20170119045622/http://www.isna.ir/'
        )
        # Todo: Make the title more accurate?
        ct = (
            '* {{cite web '
            '| title=خبرگزاری ایسنا  -  صفحه اصلی  -   ISNA News Agency '
            '| website=ایسنا '
            '| date=2017-01-19 '
            '| url=http://www.isna.ir/ '
            '| archive-url=https://web.archive.org/20170119045622/'
            'http://www.isna.ir/ '
            '| archive-date=2017-01-19 '
            '| dead-url=unfit '
            '| language=fa '
            '| ref={{sfnref | ایسنا | 2017}} '
            '| accessdate='
        )
        self.assertIn(ct, o.cite)


dummy_requests = dummy_requests.DummyRequests()
urls.requests_get = dummy_requests.get
urls.requests_head = dummy_requests.head
if __name__ == '__main__':
    unittest.main()
