"""Test urls_authors.BYLINE_PATTERN."""


from regex import compile as regex_compile, VERBOSE, IGNORECASE
from unittest import main, expectedFailure, TestCase

from lib.urls_authors import byline_to_names, BYLINE_PATTERN, \
    BYLINE_TAG_FINDITER

BYLINE_PATTERN_REGEX = regex_compile(
    '^' + BYLINE_PATTERN + '$',
    IGNORECASE | VERBOSE)


class RegexTest(TestCase):

    """BYLINE_PATTERN should pass the following tests."""

    def test_one_author(self):
        """http://www.defense.gov/News/NewsArticle.aspx?ID=18509"""
        self.assertRegex('By Jim Garamone', BYLINE_PATTERN_REGEX)

    def test_cap_names_joined_by_and(self):
        """Test two authors with and.

        Example:
        https://www.eff.org/deeplinks/2014/06/
        sudan-tech-sanctions-harm-innovation-development-us-government-and-
        corporations-must-act

        Note the two consecutive spaces.

        """
        self.assertRegex(
            'By Kimberly Carlson  and Jillian York', BYLINE_PATTERN_REGEX)

    def test_four_authors(self):
        """Test four authors, last one with and.

        http://arstechnica.com/science/2007/09/
        the-pseudoscience-behind-homeopathy/

        """
        self.assertRegex(
            'by John Timmer, Matt Ford, Chris Lee, and Jonathan Gitlin Sept',
            BYLINE_PATTERN_REGEX)

    @expectedFailure
    def test_four_authors_with_for(self):
        """Test four authors, having a "for" at the end.

        http://arstechnica.com/science/2007/09/
        the-pseudoscience-behind-homeopathy/

        """
        self.assertRegex(
            'By Sara Malm and Annette Witheridge and '
            'Ian Drury for the Daily Mail and Daniel Bates',
            BYLINE_PATTERN_REGEX)


class BylineToNames(TestCase):

    """Test byline_to_names function."""

    def test_two_author_seperated_by_comma(self):
        names = byline_to_names('\n By Roger Highfield, Science Editor \n')
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0][0], 'Roger')

    def test_in_in_byline(self):
        byline = (
            ' By Erika Solomon in Beirut and Borzou Daragahi,'
            ' Middle East correspondent'
        )
        names = byline_to_names(byline)
        self.assertEqual(len(names), 2)
        self.assertEqual(names[0][0], 'Erika')
        self.assertEqual(names[1][0], 'Borzou')

    def test_byline_ends_with_comma(self):
        names = byline_to_names('by \n Tony Smith, \n')
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0][0], 'Tony')

    def test_semicolon_seperated_names_and_for(self):
        names = byline_to_names(
            'Sara Malm;Annette Witheridge;Ian Drury for the Daily Mail;'
            'Daniel Bates')
        self.assertEqual(len(names), 4)
        self.assertEqual(names[2][0], 'Ian')
        self.assertEqual(names[2][1], 'Drury')

    def test_newline_after_and(self):
        names = byline_to_names('\nIan Sample and \nStuart Clark in Darmstadt')
        self.assertEqual(len(names), 2)
        self.assertEqual(names[1][1], 'Clark')

    def test_the_triggers_nofirst_fulllast(self):
        # https://www.nytimes.com/2016/01/08/opinion/a-shameful-round-up-of-refugees.html?_r=0
        first, last = byline_to_names('THE EDITORIAL BOARD')[0]
        self.assertEqual(first, '')
        self.assertEqual(last, 'The Editorial Board')

    def test_schema_author(self):
        # https://www.abc.net.au/news/2020-09-06/glow-worms-in-wollemi-national-park-survived-summer-bushfire/12634762
        self.assertEqual(next(BYLINE_TAG_FINDITER(
            '<script data-react-helmet="true" type="application/ld+json">'
            '{"@context":"http://schema.org","@type":"NewsArticle","author":'
            '[{"@type":"Person","name":"Kathleen Ferguson"}],'
            '"dateModified":"2020-09-07T06:34:18+00:00",'
            '"datePublished":"2020-09-06T05:26:48+00:00",'
            '"description":"An ancient species of bug, glowing on the roof of '
            'an abandoned railway tunnel deep in a remote forest, somehow '
            'managed to survive the horror Gospers Mountain bushfire and '
            'locals could not be happier.","headline":"Glow worms in Wollemi '
            'National Park survived Gospers Mountain bushfire",'
            '"image":{"@type":"ImageObject","height":485,'
            '"url":"https://www.abc.net.au/cm/rimage/12634712-16x9-xlarge.jpg?'
            'v=2","width":862},'
            '"keywords":"glow worms,wollemi national park,bushfires",'
            '"mainEntityOfPage":"https://www.abc.net.au/news/2020-09-06/glow-'
            'worms-in-wollemi-national-park-survived-summer-bushfire/12634762",'
            '"publisher":{"@type":"Organization","name":"ABC News",'
            '"logo":{"@type":"ImageObject","height":60,"url":"https://'
            'www.abc.net.au/res/abc/logos/amp-news-logo-60x240.png",'
            '"width":240}}}</script>'))['result'], 'Kathleen Ferguson')


if __name__ == '__main__':
    main()
