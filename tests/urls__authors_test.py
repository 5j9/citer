#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test urls_authors.BYLINE_PATTERN."""


import re
import unittest
import sys

sys.path.append('..')
import urls_authors


class RegexTest(unittest.TestCase):

    """BYLINE_PATTERN should pass the following tests."""

    regex = re.compile('^' + urls_authors.BYLINE_PATTERN + '$', re.IGNORECASE)

    def test_one_author(self):
        """http://www.defense.gov/News/NewsArticle.aspx?ID=18509"""
        text = 'By Jim Garamone'
        self.assertRegex(text, self.regex)

    def test_cap_names_joined_by_and(self):
        """Test two authors with and.

        Example:
        https://www.eff.org/deeplinks/2014/06/
        sudan-tech-sanctions-harm-innovation-development-us-government-and-
        corporations-must-act

        Note the two consecutive spaces.

        """
        text = 'By Kimberly Carlson  and Jillian York'
        self.assertRegex(text, self.regex)

    def test_four_authors(self):
        """Test four authors, last one with and.

        http://arstechnica.com/science/2007/09/
        the-pseudoscience-behind-homeopathy/

        """
        text = 'by John Timmer, Matt Ford, Chris Lee, and Jonathan Gitlin Sept'
        self.assertRegex(text, self.regex)

    @unittest.expectedFailure
    def test_four_authors_with_for(self):
        """Test four authors, having a "for" at the end.

        http://arstechnica.com/science/2007/09/
        the-pseudoscience-behind-homeopathy/

        """
        text = (
            'By Sara Malm and Annette Witheridge and '
            'Ian Drury for the Daily Mail and Daniel Bates'
            )
        self.assertRegex(text, self.regex)


class BylineToNames(unittest.TestCase):

    """Test byline_to_names function."""

    def test_two_author_seperated_by_comma(self):
        byline = '\n By Roger Highfield, Science Editor \n'
        names = urls_authors.byline_to_names(byline)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0].firstname, 'Roger')

    def test_in_in_byline(self):
        byline = (
            ' By Erika Solomon in Beirut and Borzou Daragahi,'
            ' Middle East correspondent'
        )
        names = urls_authors.byline_to_names(byline)
        self.assertEqual(len(names), 2)
        self.assertEqual(names[0].firstname, 'Erika')
        self.assertEqual(names[1].firstname, 'Borzou')

    def test_byline_ends_with_comma(self):
        byline = 'by \n Tony Smith, \n'
        names = urls_authors.byline_to_names(byline)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0].firstname, 'Tony')

    def test_semicolon_seperated_names_and_for(self):
        byline = (
            'Sara Malm;Annette Witheridge;Ian Drury for the Daily Mail;'
            'Daniel Bates'
        )
        names = urls_authors.byline_to_names(byline)
        self.assertEqual(len(names), 4)
        self.assertEqual(names[2].firstname, 'Ian')
        self.assertEqual(names[2].lastname, 'Drury')

    def test_newline_after_and(self):
        byline = '\nIan Sample and \nStuart Clark in Darmstadt'
        names = urls_authors.byline_to_names(byline)
        self.assertEqual(len(names), 2)
        self.assertEqual(names[1].lastname, 'Clark')
        

if __name__ == '__main__':
    unittest.main()
