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
            '| ref=harv '
            '| accessdate=2017-01-25 '
            '| archive-url=http://web.archive.org/web/20131021230444/'
            'http://www.huffingtonpost.com/2013/10/19/'
            'plastic-surgery-justin-bieber-100k_n_4128563.html?'
            'utm_hp_ref=mostpopular '
            '| archive-date=2013-10-21 '
            '| dead-url=no}}'
        )
        self.assertIn(ct, o.cite)

    def test_dead_url(self):
        """dead-url=yes"""
        i = (
            'https://web.archive.org/web/20070429193849_id/'
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
            '| ref={{sfnref | londondevelopmentcentre.org | 2007}} '
            '| accessdate=2017-01-25 '
            '| archive-url=https://web.archive.org/web/20070429193849/'
            'http://www.londondevelopmentcentre.org/page.php?s=1&p=2462 '
            '| archive-date=2007-04-29 '
            '| dead-url=yes}}'
        )
        self.assertIn(ct, o.cite)



dummy_requests = dummy_requests.DummyRequests()
urls.requests_get = dummy_requests.get
urls.requests_head = dummy_requests.head
if __name__ == '__main__':
    unittest.main()
