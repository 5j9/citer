from pytest import mark
from regex import compile as regex_compile, VERBOSE, IGNORECASE

from lib.urls_authors import byline_to_names, BYLINE_PATTERN, \
    BYLINE_TAG_FINDITER

BYLINE_PATTERN_REGEX = regex_compile(
    fr'^{BYLINE_PATTERN}$',
    IGNORECASE | VERBOSE)


def test_byline_pattern_one_author():
    """http://www.defense.gov/News/NewsArticle.aspx?ID=18509"""
    assert BYLINE_PATTERN_REGEX.search('By Jim Garamone')


def test_byline_pattern_cap_names_joined_by_and():
    """Test two authors with and.

    Example:
    https://www.eff.org/deeplinks/2014/06/
    sudan-tech-sanctions-harm-innovation-development-us-government-and-
    corporations-must-act

    Note the two consecutive spaces.

    """
    assert BYLINE_PATTERN_REGEX.search('By Kimberly Carlson  and Jillian York')


def test_byline_pattern_four_authors():
    """Test four authors, last one with and.

    http://arstechnica.com/science/2007/09/
    the-pseudoscience-behind-homeopathy/

    """
    assert BYLINE_PATTERN_REGEX.search(
        'by John Timmer, Matt Ford, Chris Lee, and Jonathan Gitlin Sept')


@mark.xfail
def test_byline_pattern_four_authors_with_for():
    """Test four authors, having a "for" at the end.

    http://arstechnica.com/science/2007/09/
    the-pseudoscience-behind-homeopathy/

    """
    assert BYLINE_PATTERN_REGEX.search(
        'By Sara Malm and Annette Witheridge and '
        'Ian Drury for the Daily Mail and Daniel Bates')


def test_byline_to_names_two_author_seperated_by_comma():
    names = byline_to_names('\n By Roger Highfield, Science Editor \n')
    assert len(names) == 1
    assert names[0][0] == 'Roger'


def test_byline_to_names_in_in_byline():
    byline = (
        ' By Erika Solomon in Beirut and Borzou Daragahi,'
        ' Middle East correspondent'
    )
    names = byline_to_names(byline)
    assert len(names) == 2
    assert names[0][0] == 'Erika'
    assert names[1][0] == 'Borzou'


def test_byline_to_names_byline_ends_with_comma():
    names = byline_to_names('by \n Tony Smith, \n')
    assert len(names) == 1
    assert names[0][0] == 'Tony'


def test_byline_to_names_semicolon_seperated_names_and_for():
    names = byline_to_names(
        'Sara Malm;Annette Witheridge;Ian Drury for the Daily Mail;'
        'Daniel Bates')
    assert len(names) == 4
    assert names[2][0] == 'Ian'
    assert names[2][1] == 'Drury'


def test_byline_to_names_newline_after_and():
    names = byline_to_names('\nIan Sample and \nStuart Clark in Darmstadt')
    assert len(names) == 2
    assert names[1][1] == 'Clark'


def test_byline_to_names_the_triggers_nofirst_fulllast():
    # https://www.nytimes.com/2016/01/08/opinion/a-shameful-round-up-of-refugees.html?_r=0
    first, last = byline_to_names('THE EDITORIAL BOARD')[0]
    assert first == ''
    assert last == 'The Editorial Board'


def test_byline_to_names_schema_author():
    # https://www.abc.net.au/news/2020-09-06/glow-worms-in-wollemi-national-park-survived-summer-bushfire/12634762
    assert next(BYLINE_TAG_FINDITER(
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
        '"width":240}}}</script>'))['result'] == 'Kathleen Ferguson'
