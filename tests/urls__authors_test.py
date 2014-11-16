#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test urls.py module."""


import re
import unittest
import sys

sys.path.append('..')
import urls_authors


class RegexTest(unittest.TestCase):
    
    """BYLINE_REGEX should pass the following tests."""

    regex = re.compile('^' + urls_authors.BYLINE_REGEX + '$', re.IGNORECASE)

    def test_one_author(self):
        """http://www.defense.gov/News/NewsArticle.aspx?ID=18509"""
        text = 'By Jim Garamone'
        self.assertRegex(text, self.regex)
        
    def test_cap_names_joined_by_and(self):
        """https://www.eff.org/deeplinks/2014/06/sudan-tech-sanctions-harm-innovation-development-us-government-and-corporations-must-act

        Note the two consecutive spaces."""
        text = 'By Kimberly Carlson  and Jillian York'
        self.assertRegex(text, self.regex)

    def test_four_authors(self):
        """http://arstechnica.com/science/2007/09/the-pseudoscience-behind-homeopathy/"""
        text = 'by John Timmer, Matt Ford, Chris Lee, and Jonathan Gitlin Sept'
        self.assertRegex(text, self.regex)

    @unittest.expectedFailure 
    def test_four_authors_with_for(self):
        """http://arstechnica.com/science/2007/09/the-pseudoscience-behind-homeopathy/"""
        text = (
            'By Sara Malm and Annette Witheridge and '
            'Ian Drury for the Daily Mail and Daniel Bates'
            )
        self.assertRegex(text, self.regex)


if __name__ == '__main__':
    unittest.main()
